# Green Mining AI

This repository contains the MVP for the Green Mining AI project developed during the AMD Slingshot Hackathon.

## 🚀 Quick start

1. **Clone and enter repo**
   ```bash
   git clone https://github.com/SKar-2007/Green-Mining-AI.git
   cd Green-Mining-AI
   ```

   #### Installing Docker

   On Linux (Ubuntu/Debian):
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose
   sudo systemctl enable --now docker
   sudo usermod -aG docker $USER   # log out and back in afterwards
   ```

   On macOS/Windows: download Docker Desktop from https://www.docker.com/
   (the rest of this guide uses `docker-compose`.)


2. **Python environment** (recommended Python 3.11)
   ```bash
   python3.11 -m venv .venv     # install python3.11 if you don't have it (3.14 also works now)
   source .venv/bin/activate
   ```
   If you prefer to skip the venv step, install the core packages manually:
   ```bash
   pip install flask flask-cors pymongo opencv-python pillow numpy requests
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt --break-system-packages
   ```
   *The full requirements include YOLO/torch which have been tested with Python 3.11 through 3.14.*

4. **Start MongoDB**
   ```bash
   sudo systemctl start mongodb
   ```

5. **Run the backend and frontend**
   ```bash
   source .venv/bin/activate
   python backend/app.py
   ```
   then open http://localhost:5000 in your browser.

6. **Optional Docker**
   Build/run with Docker Compose:
   ```bash
   cd docker
   docker-compose up --build
   ```
   (this also brings up a MongoDB container)

## � API Endpoints
- `POST /api/scan` – upload an image (multipart/form-data field `image`).
- `GET /api/scan/<scan_id>` – retrieve scan results.
- `GET /api/stats` – overall statistics, including per-category counts.
- `GET /api/components` – list component catalog entries.
- `POST /api/components` – add a new component definition (JSON body).

## �🛠️ Project structure

## 🧠 Training the YOLO model

### Generating a demo dataset

If you don't yet have real component photos, you can quickly create a
synthetic dataset to verify training and inference. A helper script is
provided; it places images under `images/` and corresponding label files
in a parallel `labels/` directory, matching the structure YOLO expects.

```bash
# create 100 training images and 20 validation images
python backend/scripts/generate_synthetic_data.py --output data/train/images --count 100
python backend/scripts/generate_synthetic_data.py --output data/val/images --count 20
```

The script draws random colored rectangles and writes YOLO-format labels.
Replace these with actual photos once available.


## 🛠️ Project structure

Training requires the `ultralytics` package. Recent versions (8.4.19+) work on Python 3.11–3.14.
There are two recommended ways to run the training script:

1. **Using the included Docker container** (preferred)
   ```bash
   # build images if you haven't already
   cd docker
   docker-compose build

   # run training inside the backend service container
   docker-compose run --rm backend python backend/scripts/train_model.py
   ```
   the container uses a python:3.11 base and has all dependencies installed.

2. **On the host machine with Python 3.11**
   ```bash
   python3.11 -m venv .venv11
   source .venv11/bin/activate
   pip install -r requirements.txt
   python backend/scripts/train_model.py
   ```

Before running, populate `data/train/images` (and `data/val/images`) with
labeled PCB/component photos and make sure `data/components.yaml` points to
those directories.

If the script cannot import `ultralytics` it will print an error and exit.

Training outputs a new weights file and also copies the best `.pt` model to
`backend/models/best.pt`. The `models` directory and any large weights are
ignored by git, so you can safely delete them or retrain as needed.


## 🛠️ Project structure
```
green-mining-ai/
├── backend/            # Flask API, model and DB code
├── frontend/           # static HTML/CSS/JS UI
├── data/               # datasets for training/validation
├── docker/             # Docker & compose files
├── .github/workflows/  # CI pipeline
├── requirements.txt
└── README.md           # this file
```

## 🧪 Testing
Use the script at `backend/scripts/test_api.py` or interact through the web interface.

## ❗ Notes
- The application falls back to an in-memory database when MongoDB is unavailable.
- For full AI detection you must have YOLOv8 model weights placed in `backend/models`.
- CI is configured to lint the backend and perform a health check on each push.

Enjoy exploring the MVP and feel free to extend it for the hackathon demo!