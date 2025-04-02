from pydantic import BaseModel
from fastapi_mail import ConnectionConfig
from dotenv import load_dotenv
import os

load_dotenv()

class EmailSettings(BaseModel):
    MAIL_USERNAME: str = "ram1236969@gmail.com"
    MAIL_PASSWORD: str = "eqhs bsyl qsob nkml"
    MAIL_FROM: str = "ram1236969@gmail.com"
    MAIL_PORT: int = 587  # Change to 587 for TLS or 465 for SSL
    MAIL_SERVER: str = "smtp.gmail.com"  # Corrected spelling
    MAIL_STARTTLS: bool = True  # Required for TLS
    MAIL_SSL_TLS: bool = False  # Required for SSL

email_settings = EmailSettings()

conf = ConnectionConfig(
    MAIL_USERNAME=email_settings.MAIL_USERNAME,
    MAIL_PASSWORD=email_settings.MAIL_PASSWORD,
    MAIL_FROM=email_settings.MAIL_FROM,
    MAIL_PORT=email_settings.MAIL_PORT,
    MAIL_SERVER=email_settings.MAIL_SERVER,
    MAIL_STARTTLS=email_settings.MAIL_STARTTLS,  # Corrected field name
    MAIL_SSL_TLS=email_settings.MAIL_SSL_TLS,  # Corrected field name
    USE_CREDENTIALS=True
)
