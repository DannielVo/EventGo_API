from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.general import schemas, crud
from app.general.services import security, verify_token

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
    return {"access_token": token, "token_type": "bearer", "role": user.role}


# router.py
@router.post("/register-attendee", response_model=dict)
def register_attendee(request: schemas.RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = crud.create_user(db, request, user_type="attendee")
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
