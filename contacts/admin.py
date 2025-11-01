from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import Contact, Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name','slug')
    search_fields = ('name',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name','email','phone','address','photo_url')
    search_fields = ('name','email')
    list_filter = ('tags',)
    actions = ['export_as_csv']

    @admin.action(description='Exportar contactos a CSV')
    def export_as_csv(self, request, queryset):
        resp = HttpResponse(content_type='text/csv; charset=utf-8')
        resp['Content-Disposition'] = 'attachment; filename=contactos.csv'
        w = csv.writer(resp)
        w.writerow(['name','email','phone','address','photo_url','tags'])
        for c in queryset:
            w.writerow([c.name, c.email, c.phone, c.address, c.photo_url, ';'.join(c.tags.values_list('name', flat=True))])
        return resp
