import cv2
import time
from ultralytics import YOLO

model = YOLO("yolo26n.pt")

camera = cv2.VideoCapture(0)

GROUP_THRESHOLD = 3
GROUP_DURATION = 5

group_start_time = None


def generate_frames():
    global group_start_time

    while True:
        success, frame = camera.read()

        if not success:
            break

        results = model(frame, verbose=False)
        result = results[0]

        people_count = 0

        if result.boxes is not None:
            for box in result.boxes:
                class_id = int(box.cls[0])

                if class_id == 0:
                    people_count += 1

        # Gathering timer
        if people_count >= GROUP_THRESHOLD:

            if group_start_time is None:
                group_start_time = time.time()

            elapsed_time = time.time() - group_start_time

        else:
            group_start_time = None
            elapsed_time = 0

        # Gathering status
        if elapsed_time >= GROUP_DURATION:
            status = "LARGE GATHERING DETECTED"
        elif people_count >= GROUP_THRESHOLD:
            status = f"Gathering check: {elapsed_time:.1f}s"
        else:
            status = "Normal"

        # Draw YOLO boxes
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
            (0, 0, 255) if elapsed_time >= GROUP_DURATION else (255, 255, 255),
            2
        )

        # Convert frame to JPEG
        ret, buffer = cv2.imencode(".jpg", annotated_frame)

        if not ret:
            continue

        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )