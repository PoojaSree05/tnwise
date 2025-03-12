from django.urls import path, include  # ✅ Ensure 'path' is imported
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('webcam_feed/', views.webcam_feed, name='webcam_feed'),
    path("maps/", views.get_nearby_hospitals, name='maps'), 
    path('accident_api/', views.accident_api, name='accident_api'),
    path('hospitals/', views.hospitals_page, name='hospitals_page'),
    path('test/', views.test, name='test'),
    path('accept/<int:id>/', views.accept, name='accept'),
    path('register/', views.register, name='register'),
    path("hospital/", views.hospital, name='hospital'),
    path('get_nearby_hospitals/', views.get_nearby_hospitals, name='get_nearby_hospitals'),
    path('send-message/', views.send_whatsapp_message, name='send_message'),

]



