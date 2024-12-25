from fastapi.responses import JSONResponse # for returning JSON responses
from fastapi.staticfiles import StaticFiles # for serving static files
from fastapi.templating import Jinja2Templates # for rendering HTML templates
from fastapi import FastAPI, Request, HTTPException # for creating the FastAPI app and handling exceptions

from selenium import webdriver # for web scraping
from selenium.webdriver.common.by import By # for locating elements
from selenium.webdriver.common.keys import Keys # for sending keys, submitting forms
from selenium.webdriver.chrome.options import Options # for setting options, configure ProxyMesh server
from selenium.webdriver.support.ui import WebDriverWait # for waiting until elements are available
from selenium.webdriver.support import expected_conditions as EC # for expected conditions
from selenium.common.exceptions import NoSuchElementException, WebDriverException # for handling scraper exceptions

import os # for fetching environment variables
import uuid # for generating unique IDs
from requests import get # for fetching the IP address
from datetime import datetime # for fetching the current date and time
from dotenv import load_dotenv # for loading environment variables from .env file
from pymongo import MongoClient # for connecting to MongoDB
from pymongo.errors import PyMongoError # for handling database errors


app = FastAPI()

load_dotenv()

PROXY_MESH = "open.proxymesh.com:31280"
USERNAME = os.getenv("TWITTER_USERNAME")
PASSWORD = os.getenv("TWITTER_PASSWORD")
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["twitter_trends"]
collection = db["trending_topics"]

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


def get_ip():
    ip = "cannot fetch IP"
    try:
        ip = get('https://api.ipify.org').text
    finally:
        return ip

def scrape_twitter(count=5):
    chrome_options = Options()
    chrome_options.add_argument(f'--proxy-server={PROXY_MESH}') # ProxyMesh proxy server
    try:
        driver = webdriver.Chrome(options=chrome_options) 
    except WebDriverException as e: # catch any WebDriver errors
        raise HTTPException(status_code=500, detail=f"Error initializing WebDriver: {e}")

    ip_address = get_ip()

    try:
        driver.get("https://twitter.com/login")

        WebDriverWait(driver, 20).until(  # Wait until the login form is available
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='text']"))
        )
        username_input = driver.find_element(By.CSS_SELECTOR, "input[name='text']")
        username_input.send_keys(USERNAME)
        username_input.send_keys(Keys.RETURN)

        WebDriverWait(driver, 20).until(  # Wait until the password input is available
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
        )
        password_input = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        password_input.send_keys(PASSWORD)
        password_input.send_keys(Keys.RETURN)
        
        WebDriverWait(driver, 20).until(  # Wait until the trends section is available
            EC.presence_of_element_located((By.CSS_SELECTOR, "section[aria-labelledby='accessible-list-0']"))
        )

        more_trends = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div/div/div/div[4]/section/div/div/div[7]/div/a")
        more_trends.click() # Click on "Show more" to get more trends. Initially, only 4 trends are shown.

        WebDriverWait(driver, 20).until(  # Wait until the trends are loaded
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/section"))
        )

        trend_names = []
        for i in range(1, count + 1):
            # primary tag, with #
            xpath_primary = f"/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/section/div/div/div[{i}]/div/div/div/div/div[2]/span/span"
            
            # non tag (fallback, trend isn't a #)
            xpath_fallback = f"/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/section/div/div/div[{i}]/div/div/div/div/div[2]/span"
            
            try: # First, try fetching the element using the primary XPath
                element = driver.find_element(By.XPATH, xpath_primary)
                trend_names.append(element.text)
                
            except NoSuchElementException:
                try: # If the primary XPath fails, try the fallback XPath (single span; trends without #)
                    element = driver.find_element(By.XPATH, xpath_fallback)
                    trend_names.append(element.text)
                    
                except NoSuchElementException as e:
                    trend_names.append("N/A")

        DaTime = datetime.now().strftime("%d-%m-%Y %H:%M:%S") # current date and time
        record = {
            "_id": f"{str(uuid.uuid4())[:10]}-{DaTime.replace(":", "").replace("-", "").replace(" ", "-")}",
            "trend1": trend_names[0],
            "trend2": trend_names[1],
            "trend3": trend_names[2],
            "trend4": trend_names[3],
            "trend5": trend_names[4],
            "timestamp": DaTime,
            "ip_address": ip_address,
        }
        try:
            collection.insert_one(record) # insert the record into the database
        except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {e}")
        
        return record # return to the frontend
    
    finally:
        driver.quit() # close the browser


@app.get("/") # Home route
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/run-script") 
async def run_script():
    try: # Run the scraper
        result = scrape_twitter()
        return JSONResponse(content=result)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"detail": f"An unexpected error occurred: {e}"}
        )
