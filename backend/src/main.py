from fastapi import FastAPI

from infrastructure.http import auth_router, health_router, user_router

app = FastAPI(title="Our site")

app.include_router(health_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
