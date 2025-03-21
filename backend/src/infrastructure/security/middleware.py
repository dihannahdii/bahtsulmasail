from typing import Optional, List
from fastapi import Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import logging
from .auth import verify_token, create_access_token, create_refresh_token
from ..config import get_settings

# Configure logging
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

class SecurityMiddleware:
    def __init__(self):
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        self.settings = settings["security"]
        self.excluded_paths = ["/api/v1/auth/login", "/api/v1/auth/refresh"]

    async def __call__(self, request: Request, call_next):
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        try:
            # Extract token from header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing or invalid authentication token",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            token = auth_header.split(" ")[1]
            token_data = verify_token(token)

            # Check token expiration
            if token_data.exp < datetime.utcnow() + timedelta(minutes=5):
                # Token is about to expire, generate new tokens
                new_access_token = create_access_token(
                    {"sub": str(token_data.user_id), "roles": token_data.roles}
                )
                new_refresh_token = create_refresh_token(
                    {"sub": str(token_data.user_id), "roles": token_data.roles}
                )

                response = await call_next(request)
                response.headers["X-New-Access-Token"] = new_access_token
                response.headers["X-New-Refresh-Token"] = new_refresh_token
                return response

            # Add user info to request state
            request.state.user = token_data
            return await call_next(request)

        except HTTPException as e:
            logger.warning(f"Authentication error: {str(e)}")
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        except Exception as e:
            logger.error(f"Unexpected error in security middleware: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"}
            )

def require_roles(roles: List[str]):
    """Decorator for role-based access control"""
    async def role_middleware(request: Request):
        user = getattr(request.state, "user", None)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        if not any(role in user.roles for role in roles):
            logger.warning(
                f"Access denied for user {user.user_id}. "
                f"Required roles: {roles}, User roles: {user.roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return True
    return role_middleware