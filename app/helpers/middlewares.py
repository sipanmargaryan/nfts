from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.helpers.database import get_db
from app.helpers.exceptions import PermissionDeniedError
from app.helpers.jwt import jwt_decode
from app.routers.auth.crud import get_active_user_by_id
from app.routers.auth.schemas import UserTokenPayload

security = HTTPBearer()

def is_logged_in_middleware():
    async def middleware(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ):
        token = credentials.credentials
        user_token_info: UserTokenPayload = UserTokenPayload(
            **jwt_decode(token)
        )
        user_info = get_active_user_by_id(db, user_token_info.user_id)
        if not user_info:
            raise PermissionDeniedError()
        return user_info

    return middleware

