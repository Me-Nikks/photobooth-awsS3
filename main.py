from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import boto3, uuid, os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.mount("/images", StaticFiles(directory="images"), name="images")
templates = Jinja2Templates(directory="templates")

# AWS S3 Config
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)
BUCKET = os.getenv("AWS_BUCKET_NAME")

@app.get("/", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # Generate a unique filename
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    contents = await file.read()

    # Upload to S3
    s3.put_object(Bucket=BUCKET, Key=filename, Body=contents, ContentType=file.content_type)

    return RedirectResponse(url="/thankyou", status_code=303)

@app.get("/thankyou", response_class=HTMLResponse)
async def thank_you(request: Request):
    return templates.TemplateResponse("thank_you.html", {"request": request})
