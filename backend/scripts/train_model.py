from ultralytics import YOLO


def train():
    # load pretrained small model
    model = YOLO('yolov8n.pt')
    results = model.train(
        data='../../data/components.yaml',
        epochs=50,
        imgsz=640,
        batch=16,
        name='ewaste_detector',
        device='cpu'  # change to 'cuda' if GPU available
    )

    metrics = model.val()
    print(f"mAP50: {metrics.box.map50}")
    print(f"mAP50-95: {metrics.box.map}")

    # save best model weight to the backend/models folder
    model.export(format='pt', imgsz=640)


if __name__ == '__main__':
    train()
