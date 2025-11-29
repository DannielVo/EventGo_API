import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

SECRET_KEY = "b65b87ae00173ebf5cd948c828707a13"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """
    Hash password using bcrypt directly - NO PASSLIB
    """
    try:
        # Convert to bytes
        password_bytes = password.encode('utf-8')
        
        # Bcrypt has a 72-byte limit, so we need to handle long passwords
        if len(password_bytes) > 72:
            logger.warning(f"Password is {len(password_bytes)} bytes, truncating to 72 bytes")
            password_bytes = password_bytes[:72]
        
        # Generate salt and hash
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)
        
        # Return as string
        return hashed_bytes.decode('utf-8')
        
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing password"
        )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password using bcrypt directly - NO PASSLIB
    """
    try:
        if not plain_password or not hashed_password:
            return False
        
        # Convert to bytes
        plain_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        # Handle long passwords for verification too
        if len(plain_bytes) > 72:
            plain_bytes = plain_bytes[:72]
        
        # Use bcrypt.checkpw directly
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
        
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password requirements
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    # Check byte length for bcrypt
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        return False, "Password is too long. Maximum 72 characters."
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    return True, "Password is valid"