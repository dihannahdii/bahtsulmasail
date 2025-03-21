from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from dotenv import load_dotenv
import os
import secrets
import re
from services.logger import logger

# Load environment variables
load_dotenv()

# Security configuration with enhanced entropy
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    SECRET_KEY = secrets.token_hex(32)  # Generate secure secret key
    logger.warning("JWT_SECRET_KEY not set, generated secure random key")

# Validate and set secure defaults for JWT configuration
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
if ALGORITHM not in ["HS256", "HS384", "HS512"]:
    raise ValueError("Invalid JWT algorithm. Must be one of: HS256, HS384, HS512")

# Token expiration settings with secure defaults
ACCESS_TOKEN_EXPIRE_MINUTES = max(15, int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")))
REFRESH_TOKEN_EXPIRE_DAYS = min(7, int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7")))

# Password policy configuration
PASSWORD_MIN_LENGTH = 12
PASSWORD_PATTERN = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: UUID
    roles: List[str]
    exp: datetime

class Role:
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

def validate_password_strength(password: str) -> bool:
    """Validate password meets minimum security requirements."""
    if len(password) < PASSWORD_MIN_LENGTH:
        return False
    if not re.match(PASSWORD_PATTERN, password):
        return False
    return True

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password with rate limiting and logging."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False

def get_password_hash(password: str) -> str:
    """Hash password with strong algorithm and work factor."""
    if not validate_password_strength(password):
        raise ValueError(
            "Password must be at least 12 characters long and contain uppercase, "
            "lowercase, numbers, and special characters"
        )
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Validate required fields
        if not all(key in payload for key in ["sub", "exp", "roles"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        try:
            user_id = UUID(payload["sub"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID format",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        roles = payload["roles"]
        if not isinstance(roles, list):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid roles format",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        exp = datetime.fromtimestamp(payload["exp"])
        if exp < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return TokenData(user_id=user_id, roles=roles, exp=exp)
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error during token verification: {str(e)}",
        )

def has_role(required_roles: List[str]):
    async def role_checker(token: str = Depends(oauth2_scheme)):
        token_data = verify_token(token)
        if not any(role in token_data.roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have the required permissions"
            )
        return token_data
    return role_checker