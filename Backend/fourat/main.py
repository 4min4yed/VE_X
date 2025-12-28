#Purpose: create app, add middleware
from fastapi import FastAPI, HTTPException, Depends #fastapi tools and error handling
from fastapi.middleware.cors import CORSMiddleware #middleware for handling CORS
from routes.auth import router as auth_router #importing the route modules

app = FastAPI(title="Simple Login API - Permanent Token") #API instance that gives you ip to get access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")