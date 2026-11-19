import datetime
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, Header
from pydantic import BaseModel, EmailStr
import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from services.common.config import JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from services.common.database import get_db, Base, engine
from services.common.models import UserModel
from services.common.middleware import ObservabilityMiddleware, setup_standard_routes
from services.common.messaging import event_bus

Base.metadata.create_all(bind=engine)

SERVICE_NAME = "auth-service"

app = FastAPI(title="User Authentication Service", version="1.0.0")
app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
setup_standard_routes(app, SERVICE_NAME)

# Schemas
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    role: Optional[str] = "customer"
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_zip: Optional[str] = None

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_zip: Optional[str] = None

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> UserModel:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid authentication token")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token verification failed or expired")

    user = db.query(UserModel).filter(UserModel.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(UserModel).filter(UserModel.email == req.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = UserModel(
        email=req.email,
        password_hash=hash_password(req.password),
        full_name=req.full_name,
        role=req.role or "customer",
        phone=req.phone,
        address_street=req.address_street,
        address_city=req.address_city,
        address_state=req.address_state,
        address_zip=req.address_zip
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})

    # Publish event
    event_bus.publish_event(
        event_type="user.registered",
        payload={"user_id": user.id, "email": user.email, "full_name": user.full_name, "role": user.role},
        source_service=SERVICE_NAME
    )

    return {
        "message": "User registered successfully",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }

@app.post("/login")
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "phone": user.phone,
            "address": {
                "street": user.address_street,
                "city": user.address_city,
                "state": user.address_state,
                "zip": user.address_zip,
                "country": user.address_country
            }
        }
    }

@app.get("/profile")
def get_profile(current_user: UserModel = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "phone": current_user.phone,
        "address": {
            "street": current_user.address_street,
            "city": current_user.address_city,
            "state": current_user.address_state,
            "zip": current_user.address_zip,
            "country": current_user.address_country
        },
        "created_at": current_user.created_at.isoformat()
    }

@app.put("/profile")
def update_profile(req: ProfileUpdateRequest, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.full_name is not None:
        current_user.full_name = req.full_name
    if req.phone is not None:
        current_user.phone = req.phone
    if req.address_street is not None:
        current_user.address_street = req.address_street
    if req.address_city is not None:
        current_user.address_city = req.address_city
    if req.address_state is not None:
        current_user.address_state = req.address_state
    if req.address_zip is not None:
        current_user.address_zip = req.address_zip

    db.commit()
    db.refresh(current_user)
    return {"message": "Profile updated successfully", "user": {"id": current_user.id, "full_name": current_user.full_name}}

@app.get("/users")
def list_users(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return [{
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "role": u.role,
        "created_at": u.created_at.isoformat()
    } for u in users]
