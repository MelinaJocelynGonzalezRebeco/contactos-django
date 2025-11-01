from django.urls import path
from . import views

app_name='contacts'
urlpatterns=[
 path('', views.contact_list, name='list'),
 path('new/', views.contact_create, name='create'),
 path('<int:pk>/edit/', views.contact_update, name='update'),
 path('<int:pk>/delete/', views.contact_delete, name='delete'),
 path('tags/new/', views.tag_create, name='tag_create'),
 path('import/', views.contact_import, name='import'),
]
