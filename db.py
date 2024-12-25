from fastapi.responses import JSONResponse # for returning JSON responses
from fastapi.staticfiles import StaticFiles # for serving static files
from fastapi.templating import Jinja2Templates # for rendering HTML templates
from fastapi import FastAPI, Request, HTTPException # for creating the FastAPI app and handling exceptions
from fastapi.responses import HTMLResponse

import os # for fetching environment variables
import uuid # for generating unique IDs
from datetime import datetime # for fetching the current date and time
from pymongo import MongoClient # for connecting to MongoDB
from pymongo.errors import PyMongoError # for handling database errors


app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["twitter_trends"]
collection = db["trending_topics"]


@app.get("/") # Home route
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/run-script") 
async def run_script():
        return "this returns the result of the scraper"


async def fetch_db_entries():
    try:
        return list(collection.find())
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.get("/db", response_class=HTMLResponse)
async def get_db_entries_html(request: Request): 
    entries = await fetch_db_entries() # Return as HTML
    return templates.TemplateResponse("db.html", {"request": request, "entries": entries})

@app.get("/db-entries")
async def get_db_entries_json(): 
    entries = await fetch_db_entries() # Return JSON
    return JSONResponse(content={"entries": entries})

@app.exception_handler(404) # handle 404 errors, when a route/path is not found
async def custom_404_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)