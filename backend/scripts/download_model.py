from ultralytics import YOLO

# download a small pretrained model for CPU demo
model = YOLO('yolov8n.pt')
print('YOLOv8n model downloaded')
