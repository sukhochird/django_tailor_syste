from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

# Admin site customization
admin.site.site_header = "Хувцас оёдлын системийн удирдлага"
admin.site.site_title = "Оёдлын систем"
admin.site.index_title = "Удирдлагын самбар"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('orders/', include('orders.urls')),
    path('customers/', include('customers.urls')),
    path('employees/', include('employees.urls')),
    path('materials/', include('materials.urls')),
    path('reports/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)