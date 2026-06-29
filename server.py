from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional
import os
import resend
import asyncio
import logging

# ---------------- CONFIG ----------------
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

resend.api_key = os.getenv("RESEND_API_KEY")

SENDER_EMAIL = os.getenv("SENDER_EMAIL", "noreply@die-lagerschachtel.de")
COMPANY_EMAIL = os.getenv("COMPANY_EMAIL", "info@die-lagerschachtel.de")

# ---------------- APP ----------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://lagerschachtel-frontend-78s6.vercel.app"
        "https://www.die-lagerschachtel.de"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api_router = APIRouter(prefix="/api")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- MODELS ----------------
class ContainerInquiry(BaseModel):
    container_size: str
    start_date: str
    end_date: Optional[str] = None
    location_area: str
    name: str
    email: EmailStr
    phone: str


class TireInquiry(BaseModel):
    tire_size: str
    tire_sets: int
    name: str
    email: EmailStr
    phone: str


class CarInquiry(BaseModel):
    car_model: str
    storage_duration: str
    name: str
    email: EmailStr
    phone: str


# ---------------- EMAIL ----------------
async def send_email(subject: str, html: str):
    try:
        params = {
            "from": SENDER_EMAIL,
            "to": [COMPANY_EMAIL],
            "subject": subject,
            "html": html
        }

        email = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent: {email.get('id')}")
        return email

    except Exception as e:
        logger.error(f"Email error: {str(e)}")
        raise


# ---------------- ROUTES ----------------
@api_router.get("/")
async def root():
    return {"status": "API running"}


@api_router.post("/inquiries/container")
async def container_inquiry(inquiry: ContainerInquiry):

    end_date = inquiry.end_date or "unbefristet"

    html = f"""
    <h2>Container Anfrage</h2>
    <p><b>Größe:</b> {inquiry.container_size}</p>
    <p><b>Start:</b> {inquiry.start_date}</p>
    <p><b>Ende:</b> {end_date}</p>
    <p><b>Ort:</b> {inquiry.location_area}</p>
    <p><b>Name:</b> {inquiry.name}</p>
    <p><b>Email:</b> {inquiry.email}</p>
    <p><b>Telefon:</b> {inquiry.phone}</p>
    """

    try:
        await send_email("Container Anfrage", html)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


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

    try:
        await send_email("Reifen Anfrage", html)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


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

    try:
        await send_email("Auto Anfrage", html)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ---------------- REGISTER ROUTER ----------------
app.include_router(api_router)