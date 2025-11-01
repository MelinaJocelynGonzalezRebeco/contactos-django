from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction
import csv, io

from .models import Contact, Tag
from .forms import ContactForm, TagForm, BulkImportForm
from .supa import upload_to_supabase, can_use_supabase

def contact_list(request):
    q = request.GET.get('q','').strip()
    tag_slug = request.GET.get('tag','').strip()
    qs = Contact.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(email__icontains=q))
    selected_tag = None
    if tag_slug:
        qs = qs.filter(tags__slug=tag_slug)
        selected_tag = Tag.objects.filter(slug=tag_slug).first()
    paginator = Paginator(qs.distinct(), 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    all_tags = Tag.objects.all()
    return render(request, 'contacts/contact_list.html', {'page_obj': page_obj, 'q': q, 'all_tags': all_tags, 'selected_tag': selected_tag, 'can_storage': can_use_supabase()})

def _save_contact_with_upload(request, form, instance=None):
    obj = form.save(commit=False)
    file = request.FILES.get('photo_file')
    if file:
        url = upload_to_supabase(file)
        if url:
            obj.photo_url = url
        else:
            messages.warning(request, 'No se pudo subir la foto a Supabase.')
    obj.save()
    form.save_m2m()
    return obj

def contact_create(request):
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES)
        if form.is_valid():
            _save_contact_with_upload(request, form)
            messages.success(request, 'Contacto creado.')
            return redirect('contacts:list')
        messages.error(request, 'Errores en el formulario.')
    else:
        form = ContactForm()
    return render(request, 'contacts/contact_form.html', {'form': form, 'title': 'Nuevo contacto'})

def contact_update(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES, instance=contact)
        if form.is_valid():
            _save_contact_with_upload(request, form, instance=contact)
            messages.success(request, 'Contacto actualizado.')
            return redirect('contacts:list')
        messages.error(request, 'Errores en el formulario.')
    else:
        form = ContactForm(instance=contact)
    return render(request, 'contacts/contact_form.html', {'form': form, 'title': 'Editar contacto'})

def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        contact.delete()
        messages.success(request, 'Contacto eliminado.')
        return redirect('contacts:list')
    return render(request, 'contacts/contact_confirm_delete.html', {'contact': contact})

def tag_create(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Etiqueta creada.')
            return redirect('contacts:list')
        messages.error(request, 'Error al crear etiqueta.')
    else:
        form = TagForm()
    return render(request, 'contacts/tag_form.html', {'form': form, 'title': 'Nueva etiqueta'})

def _get_or_create_tags(tag_str):
    tags = []
    if not tag_str: return tags
    for name in [t.strip() for t in tag_str.split(';') if t.strip()]:
        tag, _ = Tag.objects.get_or_create(name=name)
        tags.append(tag)
    return tags

def contact_import(request):
    if request.method == 'POST':
        form = BulkImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            update_existing = form.cleaned_data['update_existing']
            delimiter = form.cleaned_data['delimiter'] or ','
            try:
                content = csv_file.read().decode('utf-8-sig')
            except UnicodeDecodeError:
                content = csv_file.read().decode('latin-1')
            reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
            required = {'name','email','phone'}
            headers = set([h.strip() for h in (reader.fieldnames or [])])
            missing = required - headers
            if missing:
                messages.error(request, f"Faltan columnas requeridas: {', '.join(sorted(missing))}")
                return redirect('contacts:import')

            created=updated=skipped=0
            errors=[]
            with transaction.atomic():
                for idx, row in enumerate(reader, start=2):
                    name = (row.get('name') or '').strip()
                    email = (row.get('email') or '').strip()
                    phone = (row.get('phone') or '').strip()
                    address = (row.get('address') or '').strip()
                    photo_url = (row.get('photo_url') or '').strip()
                    tag_str = (row.get('tags') or '').strip()
                    if not (name and email and phone):
                        skipped += 1
                        errors.append(f"L{idx}: faltan name/email/phone")
                        continue
                    try:
                        if update_existing:
                            obj, created_flag = Contact.objects.update_or_create(
                                email=email,
                                defaults={'name': name, 'phone': phone, 'address': address, 'photo_url': photo_url}
                            )
                            if created_flag: created += 1
                            else: updated += 1
                        else:
                            if Contact.objects.filter(email=email).exists():
                                skipped += 1
                                continue
                            obj = Contact.objects.create(name=name, email=email, phone=phone, address=address, photo_url=photo_url)
                            created += 1
                        tags = _get_or_create_tags(tag_str)
                        if tags: obj.tags.set(tags)
                    except Exception as e:
                        errors.append(f"L{idx}: {e}")
                        skipped += 1
            msg = f"Importación: {created} creados, {updated} actualizados, {skipped} omitidos."
            if errors:
                messages.warning(request, msg + "\n" + "\n".join(errors[:5]))
            else:
                messages.success(request, msg)
            return redirect('contacts:list')
    else:
        form = BulkImportForm()
    return render(request, 'contacts/import_form.html', {'form': form})
