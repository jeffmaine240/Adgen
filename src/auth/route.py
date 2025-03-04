from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import AccessBearerAuthorization, RefreshBearerAuthorization
from src.db.redis import set_token_in_blacklist

from .model import User
from .schema import UserModel, UserLogInModel
from .service import UserService
from .utils import create_access_token, verify_password
from src.db.main import get_session

REFRESH_EXPIRY = 2
auth_router = APIRouter()
user_service = UserService()

@auth_router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserModel, db:AsyncSession=Depends(get_session)):
    user_email = user_data.email
    user_exist = await user_service.user_exist(user_email=user_email, session=db)
    print("okay")
    if not user_exist:
        new_user = await user_service.create_user(user_data=user_data,session=db)
        access_token = create_access_token(
            user_data = {
                'email': new_user.email,
                'user_uuid': str(new_user.uuid),
            }
        )
        refresh_token = create_access_token(
            user_data = {
                'email': new_user.email,
                'user_uuid': str(new_user.uuid),
            },
            refresh=True,
            expiry=timedelta(days=REFRESH_EXPIRY)
        )
        return JSONResponse(
            content={
                "message": "Registration successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "email": new_user.email,
                    "uuid": str(new_user.uuid)
                }
            }
        )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, 
        detail="User already registered, kindly log in "
    )
    

@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def user_login(user_login_data: UserLogInModel, session:AsyncSession = Depends(get_session)):
    email = user_login_data.email
    password = user_login_data.password
    check_user = await user_service.get_user_by_email(user_email=email, session=session)
    if check_user:
        password_valid = verify_password(password, check_user.hashed_password)
        if password_valid:
            access_token = create_access_token(
                user_data = {
                    'email': check_user.email,
                    'role': check_user.role, 
                    'user_uuid': str(check_user.uuid),
                }
            )

            refresh_token = create_access_token(
                user_data = {
                    'email': check_user.email,
                    'role': check_user.role,
                    'user_uuid': str(check_user.uuid),
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_EXPIRY)
            )

            return JSONResponse(
                content={
                    "message": "Login Successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "email": check_user.email,
                        "uuid": str(check_user.uuid)
                    }
                }
            )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Invalid Password"
        )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, 
        detail="User not registered, kindly sign up "
    )

@auth_router.get("/refresh", status_code=status.HTTP_201_CREATED)
async def refresh_access_token(token_data: dict = Depends(RefreshBearerAuthorization())):
    print("token_data:", token_data)
    expiry_timestamp = token_data["exp"]
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(
            user_data=token_data["user"]
        )
        return JSONResponse(
            content={
                "access_token": new_access_token
            }
        )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "message": "refresh token expired",
        }
    )


@auth_router.get("/logout", status_code=status.HTTP_200_OK)
async def revoke_access_token(token_data: dict = Depends(AccessBearerAuthorization())) -> None:
    token_jti = token_data["jti"]
    await set_token_in_blacklist(token_jti=token_jti)
    return {
        "message": "logged out successfully"
    }

# @auth_router.get("/me", status_code=status.HTTP_200_OK, response_model=UserModel)
# async def get_current_user(current_user: User = Depends(get_current_user), _ : bool = Depends(Admin_role_checker)) -> User:
#     return current_user

