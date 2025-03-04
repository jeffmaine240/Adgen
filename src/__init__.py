from fastapi import FastAPI
from src.auth.route import auth_router


version="v1"

app = FastAPI(
    title="Ad Generator api",
    version=version,
)


app.include_router(auth_router, prefix="/api/{version}/auth", tags=["auth"])

