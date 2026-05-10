import cv2
import numpy as np
from ultralytics import YOLO
import base64

# Load the YOLOv8 nano model
model = YOLO('yolov8n.pt')

# COCO classes relevant to food (YOLOv8 default classes)
# 46: banana, 47: apple, 48: sandwich, 49: orange, 50: broccoli, 
# 51: carrot, 52: hot dog, 53: pizza, 54: donut, 55: cake
FOOD_CLASSES = [46, 47, 48, 49, 50, 51, 52, 53, 54, 55]

def process_image(image_bytes):
    """
    Process image bytes, run YOLOv8 detection, and return detected items 
    along with the annotated image as a base64 string.
    """
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Run prediction
    results = model(img)
    
    detected_items = []
    
    # We only process the first result
    result = results[0]
    
    annotated_img = img.copy()
    
    # Iterate over detected boxes
    for box in result.boxes:
        cls_id = int(box.cls[0].item())
        conf = float(box.conf[0].item())
        
        # Filter for food classes and confidence > 0.3
        if cls_id in FOOD_CLASSES and conf > 0.3:
            class_name = model.names[cls_id]
            detected_items.append({
                "item_name": class_name,
                "confidence": round(conf, 2)
            })
            
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            label = f"{class_name} {conf:.2f}"
            
            # Draw rectangle and label
            cv2.rectangle(annotated_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(annotated_img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
    # Encode annotated image to base64
    _, buffer = cv2.imencode('.jpg', annotated_img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return detected_items, img_base64
