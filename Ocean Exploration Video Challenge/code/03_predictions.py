import torch
import cv2
import numpy as np

# Load YOLOv5 model from torch.hub
model = torch.hub.load('ultralytics/yolov5', 'custom', path='Model/weights/best.pt')

# Open video file
cap = cv2.VideoCapture('video.mp4')

while True:
    ret, frame = cap.read()
    if not ret:
        print('Unable to read video')
        break

    # Perform inference
    results = model(frame)

    # Parse results
    pred = results.pred[0].cpu().numpy()

    # Process detections
    for *xyxy, conf, cls in pred:
        label = f'{model.names[int(cls)]} {conf:.2f}'
        plot_one_box(xyxy, frame, label=label, color=(255, 0, 0), line_thickness=2)

    # Display the results
    cv2.imshow('YOLOv5', frame)
    if cv2.waitKey(1) == 27:  # Press 'Esc' to exit
        break

cap.release()
cv2.destroyAllWindows()

# Function to plot bounding box
def plot_one_box(x, img, color=None, label=None, line_thickness=None):
    # Plots one bounding box on image `img`
    tl = line_thickness or round(0.002 * max(img.shape[0:2])) + 1  # line/font thickness
    color = color or [random.randint(0, 255) for _ in range(3)]
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
    cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
    if label:
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(img, label, (c1[0], c1[1] - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)
