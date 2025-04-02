from fastapi import APIRouter, Request, HTTPException, Depends
from dotenv import load_dotenv
import os
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from datetime import timedelta, datetime
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi.responses import JSONResponse, RedirectResponse
import uuid
from database import get_db
from sqlalchemy.orm import Session
from model import GoogleUser, RoleTable




load_dotenv(override=True)

router = APIRouter()


oauth = OAuth()

oauth.register(
    name="Pdf",
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SCREAT"),
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    access_token_url="https://accounts.google.com/o/oauth2/token",
    access_token_params=None,
    refresh_token_url=None,
    authorize_state=os.getenv("SCREAT_KEY"),
    redirect_uri="http://127.0.0.1:8000/auth",
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    client_kwargs={"scope": "openid profile email"},
)
db: Session = Depends(get_db)
Alogrithm = "HS256"


def create_access_token(data: dict, expire_delta: timedelta):

    """
    Create JWT token 
    """

    to_encode = data.copy()

    expire = datetime.utcnow() + (expire_delta or timedelta(minutes=30))
    
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, os.getenv("JWT_SECRET_KEY"), Alogrithm)


async def current_user(request: Request):

    """
    Gets the current user and check if jwt token is expired
    """
    token = request.cookies.get("access_token")  #get access token from cookie

    if not token:
        raise HTTPException(status_code=401, detail="Not authorized") 
    
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=[Alogrithm])
        user_id = payload.get("user_id")
        email = payload.get("user_email")


        return {"user_id": user_id, "user_email": email}
    
    except ExpiredSignatureError:
        raise HTTPException(status_code=404, detail="JWT token has been expired")
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid Token")
    


@router.get("/auth")
async def auth(request: Request, db: Session = Depends(get_db)):

    """
    Gets token form google and extracts all the users info
    """

    try:
        token = await oauth.Pdf.authorize_access_token(request)
        user_info = token.get("userinfo")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Google authentication failed.")
    
    if not user_info:
        raise HTTPException(status_code=401, detail="Google authentication failed")

    expires_in = token.get("expires_in")
    user_id = user_info.get("sub")
    iss = user_info.get("iss")
    user_email = user_info.get("email")
    username = user_info.get("username")
    user_pic = user_info.get("picture")
    first_logged_in = datetime.utcnow()


    if iss not in ["https://accounts.google.com", "accounts.google.com"]:
        raise HTTPException(status_code=401, detail="Google authentication failed")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Google authentication failed")
    
    token_expire = timedelta(seconds=expires_in)

    data = {"user_id": user_id, "user_email": user_email}

    access_token = create_access_token(data, token_expire)

    session_id = str(uuid.uuid4())  #creates a unique session id when login
    log_user(user_id, username, user_email, user_pic, first_logged_in, db)
    put_role(db, user_email)


    redirect_url = request.session.pop("login_redirect", os.getenv("FRONTEND_URL")) # after login send user to frontend
    response = RedirectResponse(url=redirect_url)
    response.set_cookie(
        key="access_token", #name 
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        domain="127.0.0.1",  # Match your domain
        path="/"  # Available on all paths
    )
    return response



    

@router.get("/login")
async def login(request: Request):
    """ When this end point is exicute it will send user to the google login page """

    request.session.clear()  #clear if there is any existing session
    referer = request.headers.get("referer")
    frontend_url = os.getenv("FRONTEND_URL")
    redirect_url = os.getenv("REDIRECT_URL")
    request.session['login_redirect'] = frontend_url  #stores the frontend url
 
    return await oauth.Pdf.authorize_redirect(request, redirect_url, prompt="consent")



def log_user(user_id, username, user_email, user_pic, first_logged_in, db: Session):

    """
    store the user_info in  databaase
    """

    check_user = db.query(GoogleUser).filter(GoogleUser.user_email == user_email).first()

    if not check_user:
        google_user = GoogleUser(
            user_id=user_id,
            username=username,
            user_email=user_email,
            user_pic=user_pic,
            first_logged_in=first_logged_in,

        )

        db.add(google_user)
        
        db.commit()
    
    pass


def put_role(db: Session, user_email):

    """ store user_email with role """

    check_user = db.query(RoleTable).filter(RoleTable.user_email == user_email).first()

    if not check_user:
    
        role_table = RoleTable(
            user_email=user_email,
            role = "user"
        )

        db.add(role_table)
        db.commit()
    
    pass



@router.get("/logout")
async def logout(request: Request):
    """
    Then this endpoint is called user get logged out from the web app 
    """
    request.session.clear() #clear the session 

    response = RedirectResponse(url="/")  #return user after logout from where they came

    response.delete_cookie("access_token")

    return response

    