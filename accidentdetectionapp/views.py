from django.shortcuts import render
from django.urls import reverse
from .models import *
from django.shortcuts import render, HttpResponse
from django.http.response import StreamingHttpResponse
from accidentdetectionapp.stream import streaming
import googlemaps
import requests
import json
import vonage
import time
from .models import *
from django.shortcuts import redirect
import pusher
# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import db
# cred = credentials.Certificate('C:\\Users\\LENOVO\\projects\\Dot_Slash_Road_Safety\\smartai-3ebad-firebase-adminsdk-iwaiw-b65157f46b.json')
# firebase_admin.initialize_app(cred, {
#     'databaseURL': 'https://smartai-3ebad-default-rtdb.firebaseio.com/',
#     'databaseAuthVariableOverride': None
# })
# ref = db.reference("/")

# chdred = ref.child("Books")
# insert_data = ref.child()
# ref.set({
# 	"Books":
# 	{
# 		"Best_Sellers": -1
# 	}
# })

global hospital_name
hospital_name ="Unnamed"

from pusher_push_notifications import PushNotifications

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


def home(request):
    return render(request,'index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def webcam_feed(request):
    # print("W1")
    return StreamingHttpResponse(gen(streaming()),
					content_type='multipart/x-mixed-replace; boundary=frame')


def maps(request):
    API_KEY = 'AIzaSyBj-F7jxbhMYXYn8WuLwZpnEInBX6S4Dew'
    gmaps = googlemaps.Client(key=API_KEY)

    # Perform a nearby search for hospitals
    location = (28.4089, 77.3178)  # Latitude, Longitude
    places_result = gmaps.places_nearby(location=location, radius=5000, type='hospital')

    # Iterate through search results and display
    for place in places_result['results']:
        print("Name:", place['name'])
        print("Latitude:", place['geometry']['location']['lat'])
        print("Longitude:", place['geometry']['location']['lng'])
        print()

    return render(request, 'index.html')


# def send_mail(request):
#     client = vonage.Client(key="4627a3c9", secret="KAd19Rz2sQ7HM3Tc")
#     sms = vonage.Sms(client)
    
def hospital(request):
    return render(request,'hospital.html')

def test(request):
    global hospital_name
    notifications = Notifications.objects.all().order_by('-n_id') 
    # text = ref.child('notify').child('Notification').get()
    # accepted = ref.child('notify').child('accepted').get()
    # projectname = database.child('Data').child('Projectname').get().val()
    context = {
        'notifications': notifications,
        'hospital_name':hospital_name,
    }
    return render(request,"index2.html",context)

def accept(request,id):
    notification = Notifications.objects.filter(n_id=id).update(accepted = 1)
    send_response()
    return redirect('test')

def register(request):
    global hospital_name
    if request.method == 'POST':
        name=request.POST.get('name')
        email=request.POST.get('email')
        latitude=request.POST.get('latitude')
        longitude=request.POST.get('longitude')
        print(name,email,latitude,longitude)
        hospital=Hospital(name=name,email=email,h_lattitude=latitude,h_longitude=longitude)
        hospital.save()
        hospital_name=name
        return redirect('test')
    return render(request, 'register.html')