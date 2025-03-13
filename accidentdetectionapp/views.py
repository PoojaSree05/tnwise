from django.shortcuts import render, HttpResponse, redirect
from django.http.response import StreamingHttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from accidentdetectionapp.stream import streaming
import requests
import pusher
import pywhatkit as kit
from .models import Notifications, Hospital

# ✅ Configure Pusher
pusher_client = pusher.Pusher(
    app_id="1954040",
    key="5792836772309a1ad042",
    secret="f19fde8655bbca88f675",
    cluster="ap2",
    ssl=True
)

# ✅ Global Variable for Hospital Name
hospital_name = "Unnamed"

# ✅ Accident API Endpoint
@api_view(['POST'])
def accident_api(request):
    return Response({"message": "Accident detected successfully!"})

# ✅ Push Notification Function
def send_response(notification_id):
    pusher_client.trigger('my-channel', 'request-accepted', {
        'notification_id': notification_id,
        'message': 'Request Accepted',
    })
    print(f"✅ Push sent for notification: {notification_id}")

# ✅ Send WhatsApp Message
def send_whatsapp_message(phone_number, message):
    try:
        print("[INFO] Sending WhatsApp message...")
        kit.sendwhatmsg_instantly(phone_number, message, wait_time=20)
        print("[INFO] WhatsApp message sent successfully.")
    except Exception as e:
        print(f"[ERROR] WhatsApp message failed: {e}")

# ✅ Improved Accident Detection Logic
def process_detection(results, confidence_threshold=0.6):
    if results.empty:
        print("[DEBUG] No detection found.")
        return False

    for _, result in results.iterrows():
        if result['name'].lower() == "accident" and result['confidence'] >= confidence_threshold:
            print("[DEBUG] Valid Accident Detected!")
            return True
    return False

# ✅ YOLO Streaming with Detection
def gen(camera):
    accident_sent = False
    while True:
        jpeg_frame, raw_frame = camera.get_frame()

        if jpeg_frame is None or raw_frame is None:
            print("[ERROR] Frame is None - Skipping")
            continue

        results = camera.detect_objects(raw_frame)

        if process_detection(results) and not accident_sent:
            print("[DEBUG] Accident Detection Confirmed")

            # Save notification
            notif = Notifications(notification="Accident detected", lattitude=11.677733, longitude=78.124380, accepted=0)
            notif.save()

            send_response(notif.n_id)

            send_whatsapp_message("+916380918443","🚨 Accident Detected!/n Immediate attention required./nPlease respond Quickly!/nLive Location: https://www.google.com/maps?q=11.677733,78.12438")

            accident_sent = True

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg_frame + b'\r\n\r\n')

# ✅ Webcam Feed Endpoint
def webcam_feed(request):
    return StreamingHttpResponse(gen(streaming()), content_type='multipart/x-mixed-replace; boundary=frame')

# ✅ Home Page
def home(request):
    return render(request, 'index.html')

# ✅ Nearby Hospitals
def get_nearby_hospitals(request):
    latitude = float(request.GET.get('lat', '11.677733'))
    longitude = float(request.GET.get('lon', '78.124380'))

    nominatim_url = f"https://nominatim.openstreetmap.org/search?format=json&q=hospital&countrycodes=IN&bounded=1&viewbox={longitude-0.1},{latitude+0.1},{longitude+0.1},{latitude-0.1}&limit=10"

    try:
        response = requests.get(nominatim_url, headers={
            "User-Agent": "AccidentDetectionApp",
            "Accept-Language": "en"
        })
        hospitals = response.json()

        hospital_list = [
            {
                'name': hospital.get('display_name', 'Unknown Hospital'),
                'latitude': hospital.get('lat', ''),
                'longitude': hospital.get('lon', ''),
            } for hospital in hospitals
        ]

        return JsonResponse({'hospitals': hospital_list})

    except Exception as e:
        return JsonResponse({'error': str(e)})

# ✅ Hospital Registration Page
def hospital(request):
    return render(request, 'hospital.html')

# ✅ Hospitals Page
def hospitals_page(request):
    return render(request, 'hospitals.html')

# ✅ Notification Testing Page
def test(request):
    global hospital_name

    # Get notifications and hospitals
    notifications = Notifications.objects.all().order_by('-n_id')
    hospitals = Hospital.objects.all()

    accident_alert = "🚨 Accident detected! ✅ Request Sent to the nearest hospital."

    context = {
        'notifications': notifications,
        'hospitals': hospitals,  # Add hospital list to context
        'hospital_name': hospital_name,
        'accident_alert': accident_alert,
    }
    return render(request, "index2.html", context)

# ✅ Accept Notification
def accept(request, id):
    try:
        notification = Notifications.objects.get(n_id=id)
        notification.accepted = 1
        notification.save()

        send_response(id)
        return redirect('test')
    except Notifications.DoesNotExist:
        return JsonResponse({'error': 'Notification not found'}, status=404)

# ✅ Hospital Registration
def register(request):
    global hospital_name
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        hospital = Hospital(name=name, email=email, h_lattitude=latitude, h_longitude=longitude)
        hospital.save()

        hospital_name = name
        return redirect('test')

    return render(request, 'hospitals.html')