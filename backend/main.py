from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import os
import sys
# To temporarily deal with uploads 
import tempfile
import shutil

# Get the excel json converter
# Check if the application is running in Docker
def is_running_in_docker():
    try:
        with open("/proc/self/cgroup", "rt") as f:
            return any("docker" in line for line in f)
    except Exception as e:
        return False
running_in_docker = is_running_in_docker()
if (not running_in_docker):    
    sys.path.append("../utils/")
from utils.trial_formatter import trial_formatter


"""
import importlib

# Load the Excel utils, this isn't the most ideal code
module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/trial-formatter/trial-formatter.py'))

# Get the module name
module_name = os.path.splitext(os.path.basename(module_path))[0]

# Load the module
spec = importlib.util.spec_from_file_location(module_name, module_path)
module = importlib.util.module_from_spec(spec)
"""
app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost:8080",
    "https://schedule-genius.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility function to load JSON data
def loadJson(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

@app.get("/schedules")
async def getAllSchedules():
    sched_files = [file.name for file in Path("./data/schedules").glob("*.json")]
    schedules = []
    try:
        print("test")
        for filename in sched_files:
            path = os.path.join("./data/schedules/", filename)
            with open(path,"r") as file:
                content = json.load(file)
                schedules.append(content)
        return {"schedules": schedules}
    except:
        raise HTTPException(status_code=500, detail="Error fetching schedules")

@app.get("/schedule/{ID}")
async def getSchedule(ID: str):
    sched_files = [file.name for file in Path("./data/schedules").glob("*.json")]
    for schedule in sched_files:
        path = os.path.join("./data/schedules/", schedule)
        with open(path,"r") as file:
            if ID in file.read():
                return loadJson(path)
    
    raise HTTPException(status_code=404, detail="Schedule not found")

@app.get("/audit/{major}/{entry_year}")
async def getAudit(major: str, entry_year: str):
    try:
        #audit_data = loadJson(f"./data/audits/EY{entry_year}-{major}.json")
        audit_data = loadJson(f"./data/audits/{major}-audit.json")
        return audit_data
    except:
        raise HTTPException(status_code=500, detail="Audit file note found")


# FIXME: Critical issue, add maximum file size limit
# this should be controlled by the webserver
@app.post("/upload")
async def upload_schedule(
        file: UploadFile = File(...),
        sched_name: str = Form(...)):
    # User input is one of the trickiest things, the least we can do is 
    # verify that any uploaded documents are excel sheets and that 
    # code injection shouldn't be possible
    #valid_content_types = [
    #    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
    #    "application/vnd.ms-excel"  # .xls
    #]
    #if file.content_type not in valid_content_types:
    #    raise HTTPException(status_code=415, detail="Invalid file type. Only Excel files are allowed.")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, file.filename)
        # Save the uploaded file to the temporary directory
        with open(temp_file_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
       
        try:
            # Call the read_infosilem_format function with the file path
            schedule,_ = trial_formatter.read_infosilem_format(temp_file_path)
            sched_json = trial_formatter.convertScheduleToJson(schedule,sched_name,"U24",None)
        except:
            raise HTTPException(status_code=400, detail="Invalid Excel file")
    return sched_json


