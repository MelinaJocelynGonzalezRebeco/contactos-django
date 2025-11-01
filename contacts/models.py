from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.utils.text import slugify

phone_validator = RegexValidator(regex=r'^\+?[1-9]\d{7,14}$', message='Número de teléfono inválido.')

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    class Meta:
        ordering = ['name']
    def save(self, *a, **kw):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*a, **kw)
    def __str__(self): return self.name

class Contact(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True, validators=[EmailValidator(message='Email inválido')])
    phone = models.CharField(max_length=16, unique=True, validators=[phone_validator])
    address = models.CharField(max_length=255, blank=True)
    photo_url = models.URLField(blank=True)
    tags = models.ManyToManyField(Tag, related_name='contacts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['name']
    def __str__(self): return f"{self.name} <{self.email}>"
