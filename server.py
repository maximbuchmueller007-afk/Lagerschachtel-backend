from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from pathlib import Path
import os
import logging
import resend
import asyncio

# ---------------- CONFIG ----------------
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

resend.api_key = os.environ.get('RESEND_API_KEY', '')

SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "noreply@die-lagerschachtel.de")
COMPANY_EMAIL = os.environ.get("COMPANY_EMAIL", "info@die-lagerschachtel.de")

app = FastAPI()
api_router = APIRouter(prefix="/api")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ---------------- MODELS ----------------
class ContainerInquiry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    container_size: str
    start_date: str
    end_date: str
    location_area: str
    name: str
    email: EmailStr
    phone: str


class TireInquiry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    tire_size: str
    tire_sets: int
    name: str
    email: EmailStr
    phone: str


class CarInquiry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    car_model: str
    storage_duration: str
    name: str
    email: EmailStr
    phone: str


# ---------------- EMAIL FUNCTION ----------------
async def send_email_async(subject: str, html_content: str):
    params = {
        "from": SENDER_EMAIL,
        "to": [COMPANY_EMAIL],
        "subject": subject,
        "html": html_content
    }

    try:
        email = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent: {email.get('id')}")
        return email
    except Exception as e:
        logger.error(f"Email failed: {str(e)}")
        raise


# ---------------- ROUTES ----------------
@api_router.get("/")
async def root():
    return {"message": "Die Lagerschachtel API"}


@api_router.post("/inquiries/container")
async def container_inquiry(inquiry: ContainerInquiry):

    html = f"""
    <h2>Neue Container Anfrage</h2>
    <p><b>Container:</b> {inquiry.container_size}</p>
    <p><b>Start:</b> {inquiry.start_date}</p>
    <p><b>Mietende:</b> {inquiry.end_date}</p>
    <p><b>Ort:</b> {inquiry.location_area}</p>
    <p><b>Name:</b> {inquiry.name}</p>
    <p><b>Email:</b> {inquiry.email}</p>
    <p><b>Telefon:</b> {inquiry.phone}</p>
    """

    await send_email_async("Container Anfrage", html)
    return {"status": "success"}


@api_router.post("/inquiries/tires")
async def tire_inquiry(inquiry: TireInquiry):

    price = 20 if inquiry.tire_sets == 1 else 35

    html = f"""
    <h2>Reifen Anfrage</h2>
    <p><b>Größe:</b> {inquiry.tire_size}</p>
    <p><b>Sätze:</b> {inquiry.tire_sets}</p>
    <p><b>Preis:</b> {price}€</p>
    <p><b>Name:</b> {inquiry.name}</p>
    <p><b>Email:</b> {inquiry.email}</p>
    <p><b>Telefon:</b> {inquiry.phone}</p>
    """

    await send_email_async("Reifen Anfrage", html)
    return {"status": "success"}


@api_router.post("/inquiries/car")
async def car_inquiry(inquiry: CarInquiry):

    html = f"""
    <h2>Auto Anfrage</h2>
    <p><b>Modell:</b> {inquiry.car_model}</p>
    <p><b>Dauer:</b> {inquiry.storage_duration}</p>
    <p><b>Name:</b> {inquiry.name}</p>
    <p><b>Email:</b> {inquiry.email}</p>
    <p><b>Telefon:</b> {inquiry.phone}</p>
    """

    await send_email_async("Auto Anfrage", html)
    return {"status": "success"}


# ---------------- APP SETUP ----------------
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)