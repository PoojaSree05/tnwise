import cv2
import torch
import warnings
import numpy as np
import webbrowser
import threading
import pusher
from django.core.mail import send_mail
from django.conf import settings
from .models import Hospital, Notifications

# Suppress warnings
warnings.filterwarnings("ignore")

class streaming(object):
    def __init__(self):
        print("✅ Streaming Initialized")
        self.flag = True
        self.video_capture = cv2.VideoCapture(0)

        # Load YOLO models
        self.model1 = torch.hub.load('ultralytics/yolov5', 'custom',
                                     path='C:\\Users\\user\\Desktop\\AI\\tnwise\\best.pt',
                                     device='cpu')

        self.model2 = torch.hub.load('ultralytics/yolov5', 'custom',
                                     path="C:\\Users\\user\\Desktop\\AI\\tnwise\\accident2.pt",
                                     device='cpu')

    # Reset alert flag after 5 minutes
    def reset_flag(self):
        print("[DEBUG] Resetting alert flag.")
        self.flag = True

    # Detect objects in the frame
    def detect_objects(self, frame):
        results = self.model1(frame)
        return results.pandas().xyxy[0]

    # Main frame processing
    def get_frame(self):
        ret, frame = self.video_capture.read()
        if not ret:
            print("[ERROR] Failed to capture frame")
            return None, None

        cv2.imwrite("image.jpg", frame)
        imgs = cv2.imread("image.jpg")

        results = self.model1(imgs)
        print("[DEBUG] YOLO Model 1 Output:", results.pandas().xyxy[0])

        dummy_array = np.array(results.xyxy[0]).astype(int)

        for box in dummy_array:
            print("[DEBUG] Processing box:", box)

            if len(box) < 4 or (box[2] - box[0] < 50) or (box[3] - box[1] < 50):
                print("[DEBUG] Skipping small box.")
                continue

            # Perform accident check
            if self.check(box, imgs) and self.flag:
                print("🚨 Accident detected!")

                latitude = 11.677733
                longitude = 78.12438

                send_whatsapp_message(latitude, longitude)
                send_notification(1, True)
                send_notification(2, False)

                self.flag = False
                threading.Timer(300, self.reset_flag).start()  # Reset flag after 5 mins

        jpeg = cv2.imencode('.jpg', frame)[1]

        return jpeg.tobytes(), frame

    # Accident detection logic
    def check(self, t1, img):
        print("[DEBUG] Checking box:", t1)

        results = self.model2(img)
        print("[DEBUG] YOLO Model 2 Output:", results.pandas().xyxy[0])

        dummy_array = np.array(results.xyxy[0]).astype(int)
        dummy_array = dummy_array[dummy_array[:, 0].argsort()]

        if len(dummy_array) == 0:
            print("[DEBUG] No detections by Model 2.")
            return False

        detection = self.detect_overlap(dummy_array, t1)

        print("[DEBUG] Accident Detection Status:", detection)
        return detection

    # Check for overlapping bounding boxes
    def detect_overlap(self, boxes, t1):
        n = len(boxes)
        for i in range(n):
            x1, y1, x2, y2 = boxes[i][:4]

            for j in range(i + 1, n):
                x3, y3, x4, y4 = boxes[j][:4]

                if ((x1 <= t1[0] <= x2) or (x1 <= t1[2] <= x2)) and \
                   ((y1 <= t1[1] <= y2) or (y1 <= t1[3] <= y2)):
                    return True
        return False

    # Release video capture
    def release(self):
        self.video_capture.release()
        print("✅ Video capture released")

# Send WhatsApp notification
def send_whatsapp_message(latitude, longitude):
    try:
        phone_number = "+916380918443"
        message = f"🚨 Accident Detected!\n Immediate attention required.\nPlease respond quickly\nLive Location: https://www.google.com/maps?q={latitude},{longitude}"

        encoded_message = message.replace(" ", "%20").replace("\n", "%0A")

        whatsapp_url = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}"
        webbrowser.open(whatsapp_url)

        print("✅ WhatsApp alert sent successfully.")
    except Exception as e:
        print(f"❌ Error sending WhatsApp alert: {e}")

# Send notification via Pusher
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
        pusher_client.trigger('my-channel', 'my-event', {
            'message2': 'Urgent\nPlease send an ambulance as soon as possible at xyz address.'
        })
    elif id == 2:
        pusher_client.trigger('my-channel', 'my-event', {'request': 'Request sent'})

