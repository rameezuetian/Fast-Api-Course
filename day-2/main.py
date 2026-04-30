from fastapi import FastAPI

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