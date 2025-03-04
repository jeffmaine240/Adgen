from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Column, SQLModel, Field
from sqlalchemy.dialects import postgresql as pg

class User(SQLModel, table=True):
    __tablename__ = "users"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            pg.UUID,
            default=uuid4,
            nullable=False,
            primary_key=True
        )
    )
    email: str = Field(index=True, unique=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    role: str = Field(
        sa_column=Column(
            pg.VARCHAR,
            server_default="user",
            nullable=False
        )
    )
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(
            pg.TIMESTAMP,
            default=datetime.now,
            nullable=False,
        )
    )

    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(
            pg.TIMESTAMP,
            default=datetime.now,
            nullable=False,
        )
    )
    def __repr__(self):
        return f"<User {self.email}>"

    # alembic revision --autogenerate -m "Initial migration"
