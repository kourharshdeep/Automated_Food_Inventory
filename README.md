# FreshTrack 🥗
Automated Food Inventory and Expiry Prediction System using Image Recognition.

## Features
- **Smart Image Recognition**: Upload or capture an image of your food, and FreshTrack uses YOLOv8 to detect what it is.
- **Expiry Prediction**: Uses a hybrid approach (Rule-based + Machine Learning via Random Forest) to predict when food will expire based on type, storage condition, and past user feedback.
- **Smart Alerts**: Dashboard alerts for items expiring within 2-5 days.
- **Recipe Suggestions**: Recommends recipes based on the current contents of your inventory.
- **Continuous Learning**: Provide feedback on whether items expired early or stayed fresh to improve future predictions.

## Tech Stack
- **Frontend**: React.js, Vite, Tailwind CSS, Axios, Lucide React
- **Backend**: Python, FastAPI, Uvicorn, YOLOv8 (ultralytics), Scikit-learn, OpenCV
- **Database**: MongoDB (local or Atlas)

## Prerequisites
1. [Node.js](https://nodejs.org/) (v18+)
2. [Python](https://www.python.org/) (3.9+)
3. [MongoDB](https://www.mongodb.com/try/download/community) installed and running locally, or a MongoDB Atlas connection string.

## Installation & Setup

### 1. Database Setup
Ensure MongoDB is running locally on the default port (`localhost:27017`). If using Atlas, create a `.env` file in the `backend` folder and add:
```
MONGODB_URI=your_atlas_connection_string
```

### 2. Backend Setup
Navigate to the `backend` folder:
```bash
cd backend
```

Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the FastAPI server:
```bash
uvicorn main:app --reload --port 8001
```
The backend will be available at `http://localhost:8001`. The first time you run it and upload an image, it will download the YOLOv8n weights (~6MB).

### 3. Frontend Setup
Open a new terminal and navigate to the `frontend` folder:
```bash
cd frontend
```

Install dependencies:
```bash
npm install
```

Start the development server:
```bash
npm run dev
```
The frontend will be available at `http://localhost:5173` (or similar port indicated in the console).

## Usage Flow
1. Go to the **Upload** page and upload an image containing food items (e.g., apple, banana, pizza).
2. Review the detection results and click "Add to Inventory".
3. Navigate to **Inventory** to see your current items and their predicted expiry dates.
4. Check **Alerts** for items nearing expiry.
5. Check **Recipes** for ideas on what to cook.
6. When discarding or consuming an item, provide feedback (Thumbs Up/Down) or simply Remove it.

## Limitations
- This is a mini-project meant for demonstration. The ML model trains on a very small synthetic dataset.
- Only a predefined set of 10-15 COCO dataset food classes are recognized by the default YOLOv8 model.
