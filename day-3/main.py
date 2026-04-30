from fastapi import FastAPI , Path , HTTPException , Query
import json


app = FastAPI()

def load_data():
    
    with open("patients.json", "r") as f:
        data = json.load(f)
    return data



@app.get("/")
def read_root():
    return {"message": "Patient Management System API is running!"}

@app.get("/about")
def about():
    return {"message": "This API is designed to manage patient records and appointments."}


@app.get("/views")
def view():
    data = load_data()
    return data

@app.get("/patients/{patient_id}")
def view_patient(patient_id : str = Path(... , description="The ID of the patient to retrieve")):
    data = load_data()
    patients = data.get("patients", [])
    for patient in patients:
        if patient.get("id") == patient_id:
            return patient
    raise HTTPException(status_code = 404, detail="Patient not found")


@app.get("/sort")
def sort_patients(sort_by : str = Query(... , description="The field to sort patients by"), order : str = Query("asc", description="Sort order: asc or desc")):
    valid_fields = ['height', 'weight', 'age']
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort field. Valid fields are: {', '.join(valid_fields)}")
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail="Invalid sort order. Valid orders are: 'asc' or 'desc'")
    
    data = load_data()
    patients = data.get("patients", [])
    sorted_data = sorted(patients, key=lambda x: x.get(sort_by, 0), reverse=(order == "desc"))
    return sorted_data