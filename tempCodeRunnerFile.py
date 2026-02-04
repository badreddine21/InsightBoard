from fastapi import FastAPI, UploadFile, File,HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from test import BusinessEngine
import os
import shutil
import json

app = FastAPI()

# Allow browser communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- THE KEY ADDITION ---
# This serves index.html at http://127.0.0.1:8000/static/index.html
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    allowed_extensions = {'.csv', '.xlsx', '.xls'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(400, "Only CSV and Excel files are supported")
    temp_path = f"temp_{file.filename}_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        try:
            engine = BusinessEngine(temp_path)
            engine.load_data()
            engine.standardize_and_clean()
            engine.classify_columns()
            analysis = engine.run_analysis()
            
            report = engine.generate_json_report(analysis)
            return json.loads(report)
        except Exception as e:
            return {"error": str(e), "type": type(e).__name__}

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)