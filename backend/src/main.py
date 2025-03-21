import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.documents import router as documents_router
from routes.auth import router as auth_router

app = FastAPI(
    title="Bahtsul Masail Engine",
    description="Islamic Legal Search Engine for Bahtsul Masail Results",
    version="1.0.0"
)

# Configure CORS
origins = [
    "https://bahtsul-masail.vercel.app",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(documents_router)
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Bahtsul Masail Engine API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)