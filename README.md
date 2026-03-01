# Green Mining AI

This repository contains the MVP for the Green Mining AI project developed during the AMD Slingshot Hackathon.

## 🚀 Quick start

1. **Clone and enter repo**
   ```bash
   git clone https://github.com/SKar-2007/Green-Mining-AI.git
   cd Green-Mining-AI
   ```

2. **Python environment** (recommended Python 3.11)
   ```bash
   python3.11 -m venv .venv     # install python3.11 if you don't have it
   source .venv/bin/activate
   ```
   If you cannot create a 3.11 venv, install the core packages manually:
   ```bash
   pip install flask flask-cors pymongo opencv-python pillow numpy pandas requests
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt --break-system-packages
   ```
   *The full requirements include YOLO/torch which require Python ≤3.11.*

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