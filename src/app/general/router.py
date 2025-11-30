from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..general import schemas, crud, models
from ..general.services import security, verify_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

'''
@router.post("/register", response_model=dict)
def register_user(request: schemas.RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = crud.create_user(db, request)
        return {"message": "User created successfully", "user_id": user.user_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
'''

@router.post("/login", response_model=schemas.TokenResponse)
def login_user(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    token, user = crud.login_user(db, request.email, request.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.user_id,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone_number 
    }

@router.post("/register-attendee", response_model=dict)
def register_attendee(request: schemas.RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = crud.create_user(db, request, user_type="attendee")
        is_valid, message = crud.validate_registration_password(request.password)
        return {"message": "Attendee account created", "user_id": user.user_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/register-organizer", response_model=dict)
def register_organizer(request: schemas.RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = crud.create_user(db, request, user_type="organizer")
        return {"message": "Organizer account created", "user_id": user.user_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/protected")
def protected_route(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    return {"message": "You are authorized", "user_id": payload.get("sub")}

# === Profile ===
@router.get("/profile")
def get_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = verify_token(token)

    # Lấy user_id từ token
    user_id = payload.get("sub")

    # Lấy user từ DB
    user = db.query(models.User).filter(models.User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user.user_id,
        "email": user.email,
        "full_name": user.full_name,
        "phone_number": user.phone_number,
        "role": user.role
    }


@router.put("/profile")
def update_profile(
    request: schemas.ProfileUpdateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = verify_token(token)

    user_id = payload.get("sub")

    updated_user = crud.update_user_profile(db, user_id, request)

    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "message": "Profile updated successfully",
        "user_id": updated_user.user_id,
        "email": updated_user.email,
        "full_name": updated_user.full_name,
        "phone_number": updated_user.phone_number,
        "role": updated_user.role
    }
