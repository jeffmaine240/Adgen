from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from fastapi.exceptions import HTTPException
from fastapi import Request, status, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from .utils import decode_access_token
from src.db.redis import token_in_blacklist
from src.db.main import get_session
from .service import UserService
from .model import User
from typing import List

user_service = UserService()


class BearerAuthorization(HTTPBearer):

    def __init__(self, *, bearerFormat=None, scheme_name=None, description=None, auto_error=True):
        super().__init__(bearerFormat=bearerFormat, scheme_name=scheme_name,
                         description=description, auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        token = creds.credentials
        token_data: dict | None = decode_access_token(token)

        if not self.token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Invalid or expired token",
                    "resolution": "please get a new token"
                }
            )

        self.verify_token_data(token_data)

        if await token_in_blacklist(token_data["jti"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Token has been revoked",
                    "resolution": "please get a new token"
                }
            )

        return token_data

    def token_valid(self, token: str) -> bool:
        token_data = decode_access_token(token)
        if token_data is not None:
            return True
        return False

    def verify_token_data(self, token_data: dict | None) -> None:
        raise NotImplementedError(
            "Please override this method in the child class")


class AccessBearerAuthorization(BearerAuthorization):
    def verify_token_data(self, token_data: dict | None):
        if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="please provide an access token"
            )


class RefreshBearerAuthorization(BearerAuthorization):
    def verify_token_data(self, token_data: dict | None):
        if token_data and not token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="please provide a refresh token"
            )
        print("okay")


async def get_current_user(token_data: dict = Depends(AccessBearerAuthorization()), session: AsyncSession = Depends(get_session)) -> User:
    user_email = token_data["user"]["email"]
    user = await user_service.get_user_by_email(user_email=user_email, session=session)
    return user


# class RoleChecker:
#     def __init__(self, allowed_roles: List[str]) -> None:
#         self.allowed_roles = allowed_roles

#     def __call__(self, current_user: User = Depends(get_current_user)) -> any:
#         if current_user.role in self.allowed_roles:
#             return True
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You are not allowed to perform this action"
#         )