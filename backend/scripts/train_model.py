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
import argparse
from pathlib import Path

def train(override_epochs=None):
    # locate dataset config relative to repository root (three levels up from this script)
    repo_root = Path(__file__).parent.parent.parent.resolve()
    data_config = repo_root / 'data' / 'components.yaml'
    if not data_config.exists():
        print(f"Dataset config not found at {data_config}. Please create the data folder and add images/labels.")
        return

    # load pretrained small model (nano)
    model = YOLO('yolov8n.pt')
    print("Starting training. This may take some time...")
    # if only a handful of images present, reduce epochs for quick runs
    count = sum(len(files) for _, _, files in os.walk(os.path.dirname(data_config)))
    default_epochs = 3 if count < 200 else 50
    epochs = override_epochs if override_epochs is not None else default_epochs
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

    # copy the best weights file into backend/models for easy access
    export_path = Path(__file__).parent.parent / 'models'
    export_path.mkdir(exist_ok=True)
    # look for ultralytics output directory
    import glob, shutil
    weight_files = glob.glob('runs/detect/*/weights/best.pt')
    if weight_files:
        src = weight_files[-1]
        dst = export_path / 'best.pt'
        shutil.copy(src, dst)
        print(f"Copied best model to {dst}")
    else:
        print("Warning: could not find best.pt in runs/detect; training may have failed to save weights.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train YOLOv8 model for Green Mining AI')
    parser.add_argument('--epochs', type=int, help='override number of epochs')
    args = parser.parse_args()
    train(override_epochs=args.epochs)
