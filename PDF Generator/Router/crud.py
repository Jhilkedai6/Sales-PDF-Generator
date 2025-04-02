from fastapi import APIRouter, Depends, HTTPException,UploadFile
from .auth import current_user
from typing import Annotated
from model import Template
from database import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List
import io
from .minio import uplode_file
from weasyprint import HTML
from jinja2 import Template as JinjaTemplate
from .email import conf
from fastapi_mail import FastMail, MessageSchema, MessageType




router = APIRouter()


# Define a model for individual sales data
class SalesData(BaseModel):
    product_name: str = Field(..., example="Smartphone X")
    units_sold: int = Field(..., example=500)
    revenue: int = Field(..., example=25000)
    sales_rep: str = Field(..., example="Alice")

# Define the main report model
class SalesDetails(BaseModel):
    report_title: str = Field(..., example="Monthly Sales Report")
    report_date: datetime = Field(default_factory=datetime.utcnow, example="2025-03-29")
    total_sales: int = Field(..., example=50000)
    top_product: str = Field(..., example="Smartphone X")
    sales_data: List[SalesData] = Field(..., example=[
        {
            "product_name": "Smartphone X",
            "units_sold": 500,
            "revenue": 25000,
            "sales_rep": "Alice"
        },
        {
            "product_name": "Laptop Z",
            "units_sold": 200,
            "revenue": 20000,
            "sales_rep": "Bob"
        }
    ])



user_dependiencies = Annotated[dict, Depends(current_user)]
db_dependiencies = Annotated[Session, Depends(get_db)]

@router.get("/see")
async def see_template(db: db_dependiencies):
    """ all template"""

    temps = db.query(Template).all()
    return temps



@router.post("/Make_PDF/")
async def make_pdf(db: db_dependiencies, user: user_dependiencies, template_id: int, detail: SalesDetails):
    template_from_id = db.query(Template).filter(Template.id == template_id).first()

    if not template_from_id:
        raise HTTPException(status_code=404, detail="Template with this id not found")
    
    jinja_template = JinjaTemplate(template_from_id.template)
    rendered_html = jinja_template.render(**detail.dict())

    # Convert HTML to PDF (bytes)
    pdf_bytes = HTML(string=rendered_html).write_pdf()

    # Convert bytes to file-like object (this is important for uploading to MinIO and email)
    pdf_file = io.BytesIO(pdf_bytes)

    # Generate unique filename
    file_name = f"sales_report_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pdf"

    # Upload file to MinIO
    data = await uplode_file(file_name, pdf_bytes)

    # Create the UploadFile object to send via email
    upload_file = UploadFile(filename=file_name, file=pdf_file)

    # Set up the email message with attachment
    message = MessageSchema(
        subject="Your Sales Report",
        recipients=[user.get("user_email")],  # Send email to the user's email address
        
        # recipients=["Pyakurelprasanna2@gmail.com"],  # Send email to the user's email address

        body="Please find the attached sales report.",
        subtype=MessageType.plain,
        attachments=[upload_file]  # Attach the UploadFile object
    )

    fast_mail = FastMail(conf)
    await fast_mail.send_message(message)

    return {"message": "PDF successfully uploaded and email sent", "data": data}


# Pyakurelprasanna2@gmail.com
