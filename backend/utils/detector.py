import cv2
import numpy as np
import time

# attempt to import ultralytics; if not available, detection will be mocked
try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

class ComponentDetector:
    def __init__(self, model_path=None):
        # if a custom model path isn't provided, prefer any trained 'best.pt'
        if model_path is None:
            candidate = 'models/best.pt'
            if os.path.exists(candidate):
                model_path = candidate
            else:
                model_path = 'models/yolov8n.pt'
        # load the YOLOv8 model if available, otherwise leave as None and
        # the detection methods will return empty results or dummy data.
        if YOLO is not None:
            self.model = YOLO(model_path)
        else:
            self.model = None
        
        # simple hard-coded value lookup for MVP
        self.component_values = {
            'IC': 5.50,
            'Capacitor': 0.15,
            'Resistor': 0.02,
            'Transistor': 0.30,
            'Connector': 1.20,
            'PCB_Trace': 0.05,
            'Heat_Sink': 0.80,
            'Crystal': 0.25
        }
        
        self.recyclability_weights = {
            'IC': 90,
            'Capacitor': 70,
            'Resistor': 60,
            'Transistor': 75,
            'Connector': 80,
            'PCB_Trace': 40,
            'Heat_Sink': 95,
            'Crystal': 65
        }
    
    def preprocess_image(self, image_path):
        """Preprocess image for better detection"""
        img = cv2.imread(image_path)
        
        # Resize if too large
        max_dim = 1280
        h, w = img.shape[:2]
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            img = cv2.resize(img, None, fx=scale, fy=scale)
        
        # Enhance contrast using CLAHE
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        preprocessed_path = image_path.replace('.jpg', '_preprocessed.jpg')
        cv2.imwrite(preprocessed_path, enhanced)
        
        return preprocessed_path
    
    def detect_components(self, image_path, confidence_threshold=0.5):
        """Run detection on image"""
        start_time = time.time()
        
        processed_path = self.preprocess_image(image_path)
        
        detections = []
        if self.model is not None:
            results = self.model(processed_path, conf=confidence_threshold)
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = result.names[class_id]
                    
                    estimated_value = self.component_values.get(class_name, 0.10)
                    
                    detections.append({
                        'component': class_name,
                        'bounding_box': [int(x1), int(y1), int(x2), int(y2)],
                        'confidence': round(confidence, 3),
                        'estimated_value': estimated_value
                    })
        else:
            # no model available; return placeholder
            detections = []
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            'detections': detections,
            'processing_time': processing_time,
            'original_image': image_path
        }
    
    def save_annotated_image(self, results, output_path):
        """Save image with bounding boxes and labels"""
        if self.model is not None:
            result = self.model.predict(results['original_image'])[0]
            annotated = result.plot()
            cv2.imwrite(output_path, annotated)
        else:
            # simply copy the original file if no model
            cv2.imwrite(output_path, cv2.imread(results['original_image']))
    
    def calculate_recyclability(self, detections):
        """Calculate overall recyclability score"""
        if not detections:
            return 0
        total_score = 0
        for det in detections:
            component = det['component']
            weight = self.recyclability_weights.get(component, 50)
            total_score += weight
        avg_score = total_score / len(detections)
        return int(avg_score)
