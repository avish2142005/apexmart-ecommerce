import datetime
import re
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, Header
from pydantic import BaseModel, EmailStr, Field
import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from services.common.config import JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from services.common.database import get_db, Base, engine, apply_database_migrations
from services.common.models import UserModel
from services.common.middleware import ObservabilityMiddleware, setup_standard_routes
from services.common.messaging import event_bus

Base.metadata.create_all(bind=engine)
apply_database_migrations()

SERVICE_NAME = "auth-service"

app = FastAPI(title="User Authentication Service", version="1.0.0")
app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
setup_standard_routes(app, SERVICE_NAME)

# -----------------------------------------------------------------------------
# Validation Helper Functions & Criteria
# -----------------------------------------------------------------------------
def validate_password_criteria(password: str) -> None:
    """
    Enforces production-grade password complexity criteria:
    - Minimum 8 characters, maximum 128 characters
    - At least one lowercase letter
    - At least one uppercase letter
    - At least one digit
    - At least one special character
    - No spaces
    """
    if not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password is required."
        )
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters long."
        )
    if len(password) > 128:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password cannot exceed 128 characters."
        )
    if not re.search(r"[a-z]", password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must contain at least one lowercase letter (a-z)."
        )
    if not re.search(r"[A-Z]", password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must contain at least one uppercase letter (A-Z)."
        )
    if not re.search(r"\d", password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must contain at least one numeric digit (0-9)."
        )
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?/\\~`]", password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must contain at least one special character (e.g. !@#$%^&*)."
        )
    if " " in password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must not contain spaces."
        )

def validate_phone_criteria(phone: Optional[str]) -> Optional[str]:
    """Validates phone number criteria."""
    if not phone:
        return None
    cleaned = re.sub(r"[\s\-\(\)]", "", phone.strip())
    if not re.match(r"^\+?[1-9]\d{7,14}$", cleaned):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid mobile phone number. Please enter a valid 10-digit mobile number or international phone."
        )
    return cleaned

# -----------------------------------------------------------------------------
# Request & Response Schemas
# -----------------------------------------------------------------------------
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    role: Optional[str] = "customer"
    terms_accepted: Optional[bool] = True
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_zip: Optional[str] = None

class UserLoginRequest(BaseModel):
    email: str # Can be email address or mobile phone number
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

# -----------------------------------------------------------------------------
# API Endpoints
# -----------------------------------------------------------------------------
@app.get("/criteria")
def get_auth_criteria():
    """Returns official criteria requirements for account creation and sign-in."""
    return {
        "password_rules": [
            {"id": "min_length", "label": "At least 8 characters long", "regex": "^.{8,}$"},
            {"id": "uppercase", "label": "At least 1 uppercase letter (A-Z)", "regex": "[A-Z]"},
            {"id": "lowercase", "label": "At least 1 lowercase letter (a-z)", "regex": "[a-z]"},
            {"id": "digit", "label": "At least 1 number (0-9)", "regex": "\\d"},
            {"id": "special", "label": "At least 1 special symbol (!@#$%^&*)", "regex": "[!@#$%^&*()_+\\-=\\[\\]{}|;:,.<>?/\\\\~`]"}
        ],
        "name_rules": {
            "min_length": 3,
            "max_length": 100
        },
        "login_methods": ["email", "mobile_number"]
    }

@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    # 1. Full Name condition
    cleaned_name = req.full_name.strip()
    if len(cleaned_name) < 3:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Full name must be at least 3 characters long."
        )

    # 2. Terms acceptance condition
    if req.terms_accepted is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must agree to the Terms of Service and Conditions of Use to register."
        )

    # 3. Password criteria condition
    validate_password_criteria(req.password)

    # 4. Phone criteria condition
    cleaned_phone = validate_phone_criteria(req.phone)

    # 5. Unique Email condition
    normalized_email = req.email.strip().lower()
    existing_email = db.query(UserModel).filter(func.lower(UserModel.email) == normalized_email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists. Please sign in instead."
        )

    # 6. Unique Phone condition (if provided)
    if cleaned_phone:
        existing_phone = db.query(UserModel).filter(UserModel.phone == cleaned_phone).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this mobile number already exists."
            )

    user = UserModel(
        email=normalized_email,
        password_hash=hash_password(req.password),
        full_name=cleaned_name,
        role=req.role or "customer",
        phone=cleaned_phone,
        address_street=req.address_street,
        address_city=req.address_city,
        address_state=req.address_state,
        address_zip=req.address_zip,
        is_active=True,
        failed_login_attempts=0,
        last_login=datetime.datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})

    # Publish audit event
    event_bus.publish_event(
        event_type="user.registered",
        payload={"user_id": user.id, "email": user.email, "full_name": user.full_name, "role": user.role},
        source_service=SERVICE_NAME
    )

    return {
        "message": "Account created successfully! Welcome to ApexMart.",
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

@app.post("/login")
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    identifier = req.email.strip().lower()

    if not identifier:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or mobile phone number is required.")
    if not req.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password is required.")

    # Support login with either Email OR Phone Number
    if "@" in identifier:
        user = db.query(UserModel).filter(func.lower(UserModel.email) == identifier).first()
    else:
        cleaned_phone = re.sub(r"[\s\-\(\)]", "", identifier)
        user = db.query(UserModel).filter(
            or_(
                UserModel.phone == identifier,
                UserModel.phone == cleaned_phone,
                UserModel.phone == f"+91{cleaned_phone}"
            )
        ).first()

    # Condition 1: Check account existence
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="We cannot find an account with that email or mobile number. Please check your credentials or create an account."
        )

    # Condition 2: Check account active status
    if getattr(user, "is_active", True) is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is temporarily deactivated or suspended. Please contact customer support for assistance."
        )

    # Condition 3: Check password validity
    if not verify_password(req.password, user.password_hash):
        # Track failed attempts
        current_attempts = (getattr(user, "failed_login_attempts", 0) or 0) + 1
        user.failed_login_attempts = current_attempts
        db.commit()

        if current_attempts >= 5:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Too many incorrect password attempts. For security, please wait a moment or reset your password."
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password. Please try again."
        )

    # Login successful: Reset failed attempts & record timestamp
    user.failed_login_attempts = 0
    user.last_login = datetime.datetime.utcnow()
    db.commit()

    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})

    # Publish login audit event
    event_bus.publish_event(
        event_type="user.login",
        payload={"user_id": user.id, "email": user.email, "login_time": user.last_login.isoformat()},
        source_service=SERVICE_NAME
    )

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
        "is_active": getattr(current_user, "is_active", True),
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }

@app.put("/profile")
def update_profile(req: ProfileUpdateRequest, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.full_name is not None:
        cleaned = req.full_name.strip()
        if len(cleaned) < 3:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Full name must be at least 3 characters long.")
        current_user.full_name = cleaned
    if req.phone is not None:
        current_user.phone = validate_phone_criteria(req.phone)
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
        "phone": u.phone,
        "is_active": getattr(u, "is_active", True),
        "created_at": u.created_at.isoformat() if u.created_at else None
    } for u in users]
