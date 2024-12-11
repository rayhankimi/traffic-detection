import torch
import cv2
import time
import warnings

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

cap = cv2.VideoCapture('sample/sample.mp4')

# Constants. Change this as desired.
DESIRED_SAMPLE_RATE = 2000      # Per Milli Second
VIDEO_FRAME_RATE = 30           # Fps

FRAME_INTERVAL = int((VIDEO_FRAME_RATE * DESIRED_SAMPLE_RATE) / 1000)
DISPLAY_INTERVAL = DELAY = DESIRED_SAMPLE_RATE / 1000.0
frame_counter = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Done detecting")
        break

    frame_counter += 1

    # Process frame per frame interval
    if frame_counter % FRAME_INTERVAL == 0:
        # Detection
        results = model(frame)
        predictions = results.xyxy[0].cpu().numpy()

        detected_classes = []
        for *box, conf, cls in predictions:
            class_index = int(cls)
            detected_classes.append(class_index)

            # Draw a box (Optional)
            x1, y1, x2, y2 = map(int, box)
            label = f"{results.names[class_index]} {conf:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

        # Show the frame
        cv2.imshow("Detection", frame)

        # If there's any detected class, print the count
        if detected_classes:
            counts = {}
            for cls_idx in detected_classes:
                cls_name = class_names.get(cls_idx, "unknown")
                counts[cls_name] = counts.get(cls_name, 0) + 1

            print(counts)

        if cv2.waitKey(int(DELAY)) & 0xFF == ord('q'):
            break
        time.sleep(DISPLAY_INTERVAL)
    else:
        pass

cap.release()
cv2.destroyAllWindows()
