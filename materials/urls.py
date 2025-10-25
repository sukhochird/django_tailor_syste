from django.urls import path
from . import views

app_name = 'materials'

urlpatterns = [
    path('', views.MaterialListView.as_view(), name='material_list'),
]
