import torch
import cv2
import time
import warnings
import requests
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# YoLoV5 is deprecated, ignore warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Index mapping for class names
class_names = {
    0: "small_truck",
    1: "motorcycle",
    2: "car",
    3: "big_vehicle"
}

model = torch.hub.load(
    'ultralytics/yolov5',
    'custom',
    path='models/best.pt',
    force_reload=True
)

DEVICE_ID = 1
URL = f'{os.environ.get("url","")}api/user/device/{DEVICE_ID}/value/'
HEADERS = {
    'Authorization': 'Token ' + os.environ.get('token', '')
}

cap = cv2.VideoCapture('sample/sample.mp4')

# Constants. Change this as desired.
DESIRED_SAMPLE_RATE = 3000  # Per Milli Second
VIDEO_FRAME_RATE = 30  # Fps

FRAME_INTERVAL = int((VIDEO_FRAME_RATE * DESIRED_SAMPLE_RATE) / 1000)
DISPLAY_INTERVAL = DELAY = DESIRED_SAMPLE_RATE / 1000.0
frame_counter = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Done detecting")
        break

    frame_counter += 1

    if frame_counter % FRAME_INTERVAL == 0:
        detected_counts = {
            "small_truck": 0,
            "motorcycle": 0,
            "car": 0,
            "big_vehicle": 0
        }

        results = model(frame)
        predictions = results.xyxy[0].cpu().numpy()

        for *box, conf, cls in predictions:
            class_index = int(cls)
            class_name = class_names.get(class_index, "unknown")

            if class_name in detected_counts:
                detected_counts[class_name] += 1

        traffic_value = (detected_counts["motorcycle"] * 1 +
                         detected_counts["car"] * 3 +
                         detected_counts["small_truck"] * 4 +
                         detected_counts["big_vehicle"] * 5)

        image_name = f"image_{uuid.uuid4().hex}.jpg"
        cv2.imwrite(image_name, frame)

        json_data = {
            "value": traffic_value,
            "motorcycle_count": detected_counts["motorcycle"],
            "car_count": detected_counts["car"],
            "smalltruck_count": detected_counts["small_truck"],
            "bigtruck_count": detected_counts["big_vehicle"]
        }

        files = {
            "image": open(image_name, "rb")
        }

        # Make the POST request
        response = requests.post(URL, data=json_data, headers=HEADERS, files=files)
        print("Response:", response.status_code, response.text)

        os.remove(image_name)

        if cv2.waitKey(int(DELAY)) & 0xFF == ord('q'):
            break
        time.sleep(DISPLAY_INTERVAL)

cap.release()
cv2.destroyAllWindows()
