from django import forms
from .models import Contact, Tag

class ContactForm(forms.ModelForm):
    photo_file = forms.FileField(required=False, label='Subir foto (opcional)')
    class Meta:
        model = Contact
        fields = ['name','email','phone','address','photo_url','tags']

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']

class BulkImportForm(forms.Form):
    csv_file = forms.FileField(label="Archivo CSV")
    update_existing = forms.BooleanField(required=False, initial=False, label="Actualizar si ya existe (por email)")
    delimiter = forms.CharField(required=False, max_length=1, initial=',', label="Delimitador (por defecto ,)")
    def clean_delimiter(self):
        d = self.cleaned_data.get('delimiter') or ','
        if len(d) != 1:
            raise forms.ValidationError("El delimitador debe ser un único carácter.")
        return d
