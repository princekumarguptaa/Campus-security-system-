import cv2
import time
from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolo26n.pt")

# Open laptop camera
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Could not open camera.")
    exit()

# Gathering settings
GROUP_THRESHOLD = 3       # Minimum people
GROUP_DURATION = 5        # Seconds

group_start_time = None

while True:
    success, frame = camera.read()

    if not success:
        print("ERROR: Could not read camera frame.")
        break

    # Run YOLO
    results = model(frame, verbose=False)
    result = results[0]

    # Count people
    people_count = 0

    if result.boxes is not None:
        for box in result.boxes:

            class_id = int(box.cls[0])

            # COCO class 0 = person
            if class_id == 0:
                people_count += 1

    # TIME-BASED GROUP DETECTION

    if people_count >= GROUP_THRESHOLD:

        if group_start_time is None:
            group_start_time = time.time()

        elapsed_time = time.time() - group_start_time

    else:

        group_start_time = None
        elapsed_time = 0

    # Check if gathering lasted long enough
    group_detected = elapsed_time >= GROUP_DURATION

    # Status
    if group_detected:
        status = "LARGE GATHERING DETECTED"

    elif people_count >= GROUP_THRESHOLD:
        status = f"Gathering check: {elapsed_time:.1f}s"

    else:
        status = "Normal"

    # Draw YOLO detections
    annotated_frame = result.plot()

    # People count
    cv2.putText(
        annotated_frame,
        f"People: {people_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    # Status
    cv2.putText(
        annotated_frame,
        status,
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 255) if group_detected else (255, 255, 255),
        2
    )

    # Show camera
    cv2.imshow("CityGuard AI Camera", annotated_frame)

    # Press Q to exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()