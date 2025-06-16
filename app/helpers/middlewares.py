from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import PermissionDeniedError
from app.helpers.jwt import jwt_decode
from app.routers.auth.crud import get_active_user_by_id
from app.routers.auth.schemas import UserTokenPayload


def is_logged_in_middleware():
    async def middleware(
        Authorization: str = Header(...), db: Session = Depends(get_db)
    ):
        
        token = Authorization.replace("Bearer ", "").strip()
        
        user_token_info: UserTokenPayload = UserTokenPayload(
            **jwt_decode(token)
        )
        user_info = get_active_user_by_id(db, user_token_info.user_id)
        if not user_info:
            raise PermissionDeniedError()
        return user_info

    return middleware
