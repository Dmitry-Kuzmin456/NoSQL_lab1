import uvicorn
from fastapi import FastAPI

from infrastructure.http import auth_router, health_router, product_router, user_router

app = FastAPI(title="Our site")

app.include_router(health_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(product_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
