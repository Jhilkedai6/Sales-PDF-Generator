from fastapi import APIRouter, Depends, HTTPException, Query, Body, UploadFile
from .auth import current_user
from typing import Annotated, List
from database import get_db
from sqlalchemy.orm import Session
from model import GoogleUser, RoleTable, Template
from pydantic import BaseModel, Field
from datetime import datetime
from jinja2 import Template as JinjaTemplate
from weasyprint import HTML
from fastapi.responses import Response
from .minio import uplode_file
import io
from .email import conf
from fastapi_mail import FastMail, MessageSchema, MessageType
from .audit import audit
from model import Audit


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

user_dependiencies = Annotated[dict, Depends(current_user)]
db_dependiencies = Annotated[Session, Depends(get_db)]

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



@router.put("/Add_Template/")
async def add_template(user: user_dependiencies, db: Session = Depends(get_db), Name: str = Query(...), template: str = Body(..., media_type="text/plain")):
    """ Add Html template on Database """
    
    user = db.query(GoogleUser).filter(GoogleUser.user_email == user.get("user_email")).first()
    role = db.query(RoleTable).filter(RoleTable.user_email == user.user_email).first()

    if role.role != "user":
        raise HTTPException(status_code=401, detail="Unauthorized")

    temp = Template(
        template_name=Name,
        template=template,
        added_at=datetime.utcnow()
    )

    await audit(db, user_id=user.user_id, user_email=user.user_email, activity="Template_Added")

    db.add(temp)
    db.commit()

    return "Template has been added"
    

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

    # Convert bytes to file-like object
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
        body="Please find the attached sales report.",
        subtype=MessageType.plain,
        attachments=[upload_file]  # Attach the UploadFile object
    )

    fast_mail = FastMail(conf)
    await fast_mail.send_message(message)

    return {"message": "PDF successfully uploaded", "data": data}


@router.delete("/delete/")
async def delete_template(user: user_dependiencies, db: db_dependiencies, id: int):
    """ Delete templates with template id """

    user = db.query(GoogleUser).filter(GoogleUser.user_email == user.get("user_email")).first()
    role = db.query(RoleTable).filter(RoleTable.user_email == user.user_email).first()

    if role.role != "user":
        raise HTTPException(status_code=401, detail="Unauthorized")

    temp = db.query(Template).filter(Template.id ==  id).first()

    await audit(db, user_email=user.user_email, user_id=user.user_id, activity=f"Template deleted temp_id: {temp.id}")

    db.delete(temp)
    db.commit()


    return "Template has been deleted"



@router.get("/See_Audit_Logs/")
async def see_audit_logs(db: db_dependiencies,
                          Skip: int = Query(0, ge=0, description="Number of item to skip"), 
                          limit: int = Query(10, ge=0, le=20, description="Number of items to show")):

    audits = db.query(Audit).offset(Skip).limit(limit).all()

    return audits


