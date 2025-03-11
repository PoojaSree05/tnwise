import cv2
import torch
import warnings
import time
import numpy as np
import webbrowser
import pusher
from django.core.mail import send_mail
from django.conf import settings
from .models import Hospital, Notifications

# Suppress warnings
warnings.filterwarnings("ignore")

# Function to check accident detection
def check(t1, img, model):
    results = model(img)
    results.print()
    dummy_array = np.array(results.xyxy[0]).astype(int)
    dummy_array = dummy_array[dummy_array[:, 0].argsort()]
    return detect(dummy_array, t1)

# Function to send notifications via Pusher
def send_notification(id, flag):
    pusher_client = pusher.Pusher(
        app_id='1328110',
        key='4da6311b184ace45d1dc',
        secret='469709e6b17fadfab16f',
        cluster='ap2',
        ssl=True
    )
    if flag:
        notif = Notifications(notification="Accident happened", lattitude=47.5, longitude=122.33, accepted=0)
        notif.save()
    if id == 1:
        pusher_client.trigger('my-channel', 'my-event', {'message2': 'Urgent\nPlease send an ambulance as soon as possible at xyz address.'})
    elif id == 2:
        pusher_client.trigger('my-channel', 'my-event', {'request': 'Request Sent'})

# Function to detect overlapping bounding boxes
def detect(boxes, t1):
    n = len(boxes)
    for i in range(n):
        x1, y1, x2, y2 = boxes[i][:4]

        for j in range(i + 1, n):
            x3, y3, x4, y4 = boxes[j][:4]
            
            xmin, xmax = min(x1, x3), max(x2, x4)
            ymin, ymax = min(y1, y3), max(y2, y4)

            if ((xmin <= t1[0] <= xmax) or (xmin <= t1[2] <= xmax)) and \
               ((ymin <= t1[1] <= ymax) or (ymin <= t1[3] <= ymax)):
                return True
    return False

# Function to send WhatsApp alert with location
def send_whatsapp_message(latitude, longitude):
    try:
        phone_number = "+916380918443"  # Recipient's WhatsApp number
        message = f"Accident Detected! 🚨 \nImmediate attention required. \nPlease respond quickly!\nLive Location: https://www.google.com/maps?q={latitude},{longitude}"

        # Encode the message for the URL
        encoded_message = message.replace(" ", "%20").replace("\n", "%0A")

        # Force opening WhatsApp Web
        whatsapp_url = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}"

        # Open WhatsApp Web
        webbrowser.open(whatsapp_url)

        print("✅ WhatsApp Web opened successfully with live location.")
    except Exception as e:
        print(f"❌ Error opening WhatsApp Web: {e}")

# Streaming class for accident detection
class streaming(object):
    def __init__(self):
        print("Hello, Streaming initialized")
        self.flag = True
        self.video_capture = cv2.VideoCapture(0)

        # Load accident detection models
        self.model1 = torch.hub.load('ultralytics/yolov5', 'custom',
                             path='C:\\Users\\M.Sruthi\\Desktop\\tnwise\\tnwise\\best.pt',
                             device='cpu')

        self.model = torch.hub.load('ultralytics/yolov5', 'custom',
                            path='C:\\Users\\M.Sruthi\\Desktop\\tnwise\\tnwise\\accident2.pt',
                            device='cpu')




    # Function to get video frames
    def get_frame(self):
        ret, frame = self.video_capture.read()
        if not ret:
            return None
        
        cv2.imwrite("image.jpg", frame)
        imgs = cv2.imread("image.jpg")

        # Run model inference
        results = self.model1(imgs)
        results.print()

        dummy_array = np.array(results.xyxy[0]).astype(int)

        # Process detections
        for box in dummy_array:
            if check(box, imgs, self.model) and self.flag:
                print("&" * 40)
                print("🚨 Accident detected!")

                # Example accident location (Replace with real GPS data)
                latitude = 11.677733
                longitude = 78.12438

                # Send WhatsApp message with location
                send_whatsapp_message(latitude, longitude)

                # Send push notifications
                send_notification(1, True)
                send_notification(2, False)

                self.flag = False  # Avoid duplicate notifications

        jpeg = cv2.imencode('.jpg', frame)[1]
        return jpeg.tobytes()

