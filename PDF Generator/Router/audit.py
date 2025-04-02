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
from model import Audit
from datetime import datetime




user_dependiencies = Annotated[dict, Depends(current_user)]
db_dependiencies = Annotated[Session, Depends(get_db)]




async def audit(db: Session, user_id: int, user_email: str, activity: str):

    
    log = Audit(
        user_id=user_id,
        user_email=user_email,
        activity=activity,
        time=datetime.utcnow()
    )

    db.add(log)
    db.commit()
