import base64
from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import datetime
from bson import ObjectId

from database import food_items_collection, feedback_collection
from detection import process_image
from expiry import predict_expiry
from recipes import suggest_recipes

app = FastAPI(title="FreshTrack API")

# Allow CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request bodies
class InventoryItem(BaseModel):
    item_name: str
    quantity: int = 1
    storage_type: str = "fridge" # fridge, pantry, freezer
    confidence: float

class Feedback(BaseModel):
    item_id: str
    feedback_score: int # -1, 0, 1

# Helper to serialize MongoDB object IDs
def serialize_doc(doc):
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    
    contents = await file.read()
    
    try:
        detected_items, annotated_image = process_image(contents)
        return {
            "detected_items": detected_items,
            "annotated_image": f"data:image/jpeg;base64,{annotated_image}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.websocket("/ws/track")
async def websocket_track(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if "," in data:
                data = data.split(",")[1]
            try:
                image_bytes = base64.b64decode(data)
                detected_items, annotated_image = process_image(image_bytes)
                await websocket.send_json({
                    "detected_items": detected_items,
                    "annotated_image": f"data:image/jpeg;base64,{annotated_image}"
                })
            except Exception as e:
                await websocket.send_json({"error": str(e)})
    except WebSocketDisconnect:
        print("Client disconnected from tracking WebSocket")

@app.post("/add-to-inventory")
async def add_to_inventory(items: List[InventoryItem]):
    added_items = []
    now = datetime.datetime.utcnow()
    
    for item in items:
        # Determine expiry
        storage_cond = 1 if item.storage_type == "fridge" else 0
        expiry_days = predict_expiry(item.item_name, storage_condition=storage_cond, days_since_added=0)
        expiry_date = now + datetime.timedelta(days=expiry_days)
        
        doc = {
            "item_name": item.item_name,
            "quantity": item.quantity,
            "storage_type": item.storage_type,
            "confidence": item.confidence,
            "date_added": now,
            "expiry_date": expiry_date,
            "status": "fresh"
        }
        
        result = food_items_collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        added_items.append(serialize_doc(doc))
        
    return {"message": f"Successfully added {len(added_items)} items.", "items": added_items}

@app.get("/get-inventory")
async def get_inventory():
    items = list(food_items_collection.find())
    return [serialize_doc(item) for item in items]

@app.get("/get-recipes")
async def get_recipes():
    items = list(food_items_collection.find())
    return suggest_recipes(items)

@app.get("/get-alerts")
async def get_alerts():
    items = list(food_items_collection.find())
    alerts = []
    now = datetime.datetime.utcnow()
    
    for item in items:
        days_remaining = (item["expiry_date"] - now).days
        
        if days_remaining <= 2:
            alert_type = "red"
        elif days_remaining <= 5:
            alert_type = "yellow"
        else:
            alert_type = "green"
            
        if alert_type in ["red", "yellow"]:
            alerts.append({
                "id": str(item["_id"]),
                "item_name": item["item_name"],
                "days_remaining": days_remaining,
                "alert_type": alert_type
            })
            
    return alerts

@app.post("/submit-feedback")
async def submit_feedback(feedback: Feedback):
    try:
        obj_id = ObjectId(feedback.item_id)
        item = food_items_collection.find_one({"_id": obj_id})
        
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
            
        now = datetime.datetime.utcnow()
        days_since_added = (now - item["date_added"]).days
        storage_cond = 1 if item["storage_type"] == "fridge" else 0
        
        feedback_doc = {
            "item_id": feedback.item_id,
            "food_type": item["item_name"],
            "storage_condition": storage_cond,
            "days_since_added": days_since_added,
            "user_feedback_score": feedback.feedback_score,
            "timestamp": now
        }
        
        feedback_collection.insert_one(feedback_doc)
        return {"message": "Feedback submitted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/remove-item/{item_id}")
async def remove_item(item_id: str):
    try:
        result = food_items_collection.delete_one({"_id": ObjectId(item_id)})
        if result.deleted_count == 1:
            return {"message": "Item removed successfully."}
        else:
            raise HTTPException(status_code=404, detail="Item not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
