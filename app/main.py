from fastapi import FastAPI
from app.router.auth import router
from app.database.database import Base, engine
from app.middleware.token import jwt_middleware
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.middleware("http")(jwt_middleware)
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

app.include_router(router, prefix="/auth", tags=["auth"])