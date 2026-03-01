# training script for YOLOv8 model
# This file is intended to be run either in a Python 3.11 environment
# (see README) or inside the Docker container (which uses 3.11-slim).

try:
    from ultralytics import YOLO
except ImportError:
    print("ERROR: ultralytics/Yolov8 library not available.\n"
          "Please run this script with Python 3.11 or inside the docker container.\n"
          "Example: docker-compose run --rm backend python backend/scripts/train_model.py")
    exit(1)

import os


def train():
    data_config = os.path.join(os.getcwd(), '..', '..', 'data', 'components.yaml')
    if not os.path.exists(data_config):
        print(f"Dataset config not found at {data_config}. Please create the data folder and add images/labels.")
        return

    # load pretrained small model (nano)
    model = YOLO('yolov8n.pt')
    print("Starting training. This may take some time...")
    # if only a handful of images present, reduce epochs for quick runs
    count = sum(len(files) for _, _, files in os.walk(os.path.dirname(data_config)))
    epochs = 3 if count < 200 else 50
    print(f"Using {epochs} epochs (dataset count {count})")
    results = model.train(
        data=data_config,
        epochs=epochs,
        imgsz=640,
        batch=16,
        name='ewaste_detector',
        device='cpu'  # change to 'cuda' if GPU available
    )

    metrics = model.val()
    print(f"mAP50: {metrics.box.map50}")
    print(f"mAP50-95: {metrics.box.map}")

    # save best model weight to the backend/models folder
    export_path = os.path.join('..', 'models')
    os.makedirs(export_path, exist_ok=True)
    model.export(format='pt', imgsz=640, directory=export_path)
    print(f"Model exported to {export_path}")


if __name__ == '__main__':
    train()
