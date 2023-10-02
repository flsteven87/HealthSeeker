from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('diagnosis/', views.diagnosis, name='diagnosis'),
    path('diagnosis/register/', views.register_endpoint, name='register_endpoint'),  # 修改URL
]
