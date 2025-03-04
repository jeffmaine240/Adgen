from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from sqlmodel import select
# import passlib

from .schema import UserModel
from .model import User
from .utils import generate_password_hash

class UserService:

    async def create_user(self, user_data: UserModel, session: AsyncSession):
        user_data_dict = user_data.model_dump()
        user_data_dict["hashed_password"] = generate_password_hash(user_data.password)
        new_user = User(**user_data_dict)
        session.add(new_user)
        await session.commit()
        return new_user

    async def get_user_by_email(self, user_email: str, session: AsyncSession):
        statement = select(User).where(User.email == user_email)
        result = await session.exec(statement=statement)
        return result.first()
    
    async def user_exist(self, user_email: str, session: AsyncSession):
        user = await self.get_user_by_email(user_email=user_email, session=session)
        if user:
            return True
        return False

    async def delete_user(self, user_email:str, session:AsyncSession):
        user_to_delete = await self.get_user_by_email(session=session, user_email=user_email)
        if user_to_delete:
            await session.delete(user_to_delete)
            await session.commit()
            return {}
        return None

