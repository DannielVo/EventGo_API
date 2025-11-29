from sqlalchemy.orm import Session
from ..general import models, schemas
from ..general.services import hash_password, verify_password, create_access_token

# Tạo user mới
def create_user(db: Session, user_data: schemas.RegisterRequest, user_type: str):
    existing = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing:
        raise ValueError("Email already registered")

    hashed_pw = hash_password(user_data.password)
    user = models.User(
        email=user_data.email,
        password_hash=hashed_pw,
        full_name=user_data.full_name,
        phone_number=user_data.phone_number,
        #role=user_data.role,
        role=user_type,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

     # Nếu là organizer thì tạo record trong organizers
    if user_type == "organizer":
        organizer = models.Organizer(user_id=user.user_id, company_name="")
        db.add(organizer)
        db.commit()
    
    return user


# Đăng nhập
def authenticate_user(db: Session, email: str, password: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


# Tạo token
def login_user(db: Session, email: str, password: str):
    user = authenticate_user(db, email, password)
    if not user:
        return None, None

    token = create_access_token({"sub": str(user.user_id), "email": user.email, "role": user.role})
    return token, user


# Update profile
def update_user_profile(db: Session, user_id: int, update_data: schemas.ProfileUpdateRequest):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()

    if not user:
        return None

    if update_data.full_name is not None:
        user.full_name = update_data.full_name

    if update_data.phone_number is not None:
        user.phone_number = update_data.phone_number

    db.commit()
    db.refresh(user)
    return user


# Add this to your crud.py or registration endpoint
def validate_registration_password(password: str) -> tuple[bool, str]:
    """
    Comprehensive password validation for registration
    """
    # Check minimum length
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    # Check maximum bytes for bcrypt
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        return False, "Password is too long. Please use a shorter password."
    
    # Check for uppercase
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for lowercase
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for digit
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    return True, "Password is valid"