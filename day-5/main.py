from fastapi import FastAPI , Path , HTTPException , Query , JSONResponse
import json
from pydantic import BaseModel , Field , computed_field
from typing import List , Optional , Annotated ,Literal

app = FastAPI()

class Patient(BaseModel):
    id : Annotated[str, Field(...,description="The unique identifier for the patient")]
    name : Annotated[str, Field(...,description="The full name of the patient")]
    city :  Annotated[str, Field(...,description="The city where the patient resides")]
    age : Annotated[int , Field(..., gt = 0 , lt = 120 , description="The age of the patient (must be between 1 and 120)")]
    gender : Annotated[Literal["male","female","other"], Field(..., description="The gender of the patient (must be 'male', 'female', or 'other')")]
    height : Annotated[float, Field(..., gt=0, description="The height of the patient in centimeters (must be greater than 0)")]
    weight : Annotated[float, Field(..., gt=0, description="The weight of the patient in kilograms (must be greater than 0)")]

    @computed_field
    @property
    def bmi(self) -> float:
        height_in_meters = self.height / 100
        return round(self.weight / (height_in_meters ** 2), 2)
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif 18.5 <= self.bmi < 25:
            return "Normal weight"
        elif 25 <= self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"




class PatienUpdate(BaseModel):
    name : Optional[Annotated[str, Field(None,description="The full name of the patient")]]
    city :  Optional[Annotated[str, Field(None,description="The city where the patient resides")]]
    age : Optional[Annotated[int , Field(None, gt = 0 , lt = 120 , description="The age of the patient (must be between 1 and 120)")]]
    height : Optional[Annotated[float, Field(None, gt=0, description="The height of the patient in centimeters (must be greater than 0)")]]
    weight : Optional[Annotated[float, Field(None, gt=0, description="The weight of the patient in kilograms (must be greater than 0)")]]
     
    




def load_data():
    
    with open("patients.json", "r") as f:
        data = json.load(f)
    return data

def save_data(data):
    with open("patients.json", "w") as f:
        json.dump(data, f, indent=4)


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

@app.post("/create")
def create_patient(patient: Patient):
    data = load_data()
    patients = data.get("patients" , [])
    
    if patient.id in [p.get("id") for p in patients]:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists")
    
    data[patient.id] = patient.model_dump(exclude=['id'])
    save_data(data)
    return JSONResponse(content={"message": "Patient created successfully"}, status_code=201)


@app.put("edit/{patient_id}")
def update_patient(patient_id : str = Path(... , description="The ID of the patient to update") , patient_update : PatienUpdate = ...):
    data = load_data()
    patients = data.get("patients", [])
    
    for patient in patients:
        if patient.get("id") == patient_id:
            updated_patient = patient.copy()
            update_data = patient_update.model_dump(exclude_unset=True)
            updated_patient.update(update_data)
            data["patients"] = [updated_patient if p.get("id") == patient_id else p for p in patients]
            save_data(data)
            return JSONResponse(content={"message": "Patient updated successfully"}, status_code=200)
    
    raise HTTPException(status_code=404, detail="Patient not found")


@app.delete("/delete/{patient_id}")
def delete_patient(patient_id : str = Path(... , description="The ID of the patient to delete")):
    data = load_data()
    patients = data.get("patients", [])
    
    for patient in patients:
        if patient.get("id") == patient_id:
            data["patients"] = [p for p in patients if p.get("id") != patient_id]
            save_data(data)
            return JSONResponse(content={"message": "Patient deleted successfully"}, status_code=200)
    
    raise HTTPException(status_code=404, detail="Patient not found")