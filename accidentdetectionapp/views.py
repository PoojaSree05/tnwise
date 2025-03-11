from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse
from django.http.response import StreamingHttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from accidentdetectionapp.stream import streaming
import googlemaps
import requests
import json
import time
import pusher
from pusher_push_notifications import PushNotifications
from .models import *

# Accident API Endpoint
@api_view(['POST'])
def accident_api(request):
    return Response({"message": "🚨 Accident Detected! Immediate attention required. Please respond quickly!"})


# Push Notification Function
def send_response():
    push_client = PushNotifications(
        instance_id='YOUR_INSTANCE_ID',
        secret_key='YOUR_SECRET_KEY',
    )

    response = push_client.publish(
        interests=['my-channel'],
        publish_body={
            'web': {
                'notification': {
                    'title': 'Accident Alert!',
                    'body': 'Request Accepted',
                },
            },
        },
    )
    print("Push sent:", response)

# Global Variable for Hospital Name
global hospital_name
hospital_name = "Unnamed"

# Home Page
def home(request):
    return render(request, 'index.html')

# Streaming Webcam Feed
def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def webcam_feed(request):
    return StreamingHttpResponse(gen(streaming()), content_type='multipart/x-mixed-replace; boundary=frame')

# Google Maps API for Nearby Hospitals
def maps(request):
    API_KEY = 'YOUR_GOOGLE_MAPS_API_KEY'  # <-- Replace this with settings.py reference
    gmaps = googlemaps.Client(key=API_KEY)

    location = (28.4089, 77.3178)  # Latitude, Longitude
    places_result = gmaps.places_nearby(location=location, radius=5000, type='hospital')

    # Print hospital details (for debugging)
    for place in places_result['results']:
        print("Name:", place['name'])
        print("Latitude:", place['geometry']['location']['lat'])
        print("Longitude:", place['geometry']['location']['lng'])
        print()

    return render(request, 'index.html')

# Hospital Page
def hospital(request):
    return render(request, 'hospital.html')

# Test Page (Displays Notifications)
def test(request):
    global hospital_name
    notifications = Notifications.objects.all().order_by('-n_id')

    context = {
        'notifications': notifications,
        'hospital_name': hospital_name,
    }
    return render(request, "index2.html", context)

# Accept Notification Request
def accept(request, id):
    Notifications.objects.filter(n_id=id).update(accepted=1)
    send_response()
    return redirect('test')

# Register a New Hospital
def register(request):
    global hospital_name
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        print(name, email, latitude, longitude)
        hospital = Hospital(name=name, email=email, h_lattitude=latitude, h_longitude=longitude)
        hospital.save()
        hospital_name = name

        return redirect('test')

    return render(request, 'register.html')

