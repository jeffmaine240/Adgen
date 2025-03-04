from pydantic import BaseModel, EmailStr

class UserModel(BaseModel):
    email:str
    password:str
    first_name:str
    last_name:str
    role: str = "product_owner"


class UserLogInModel(BaseModel):
    email:str
    password:str

# class UserBase(BaseModel):
#     email: EmailStr
#     full_name: str | None = None
#     role: str = "product_owner"

# # Schema for user creation (includes password)
# class UserCreate(UserBase):
#     password: str

# # Schema for response (hides password)
# class UserResponse(UserBase):
#     id: str
#     is_active: bool

#     class Config:
#         from_attributes = True 