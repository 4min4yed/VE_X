from fastapi import FastAPI, HTTPException #fastapi tools and error handling
from fastapi.security import httpBearer, HTTPAuthorizationCredentials #security tools for handling bearer tokens
from pydantic import BaseModel #validation of the data (password and email)
from jose import jwt #JWT creation and verification

app = FastAPI(title="Simple Login API - Permanent Token") #API instance that gives you ip to get access 

# Fake user (in memory)
FAKE_USER = {
    "id": 1,
    "email": "user@example.com",
    "password": "12345"
}
# Fake database (in memory)
USERS = []

SECRET_KEY = "supersecret" # Secret key for JWT
ALGORITHM = "HS256" # Algorithm used for JWT

class LoginRequest(BaseModel): #data model for login request
    email: str
    password: str

def create_token(user_id: int, email: str): #function to create JWT token
    # No "exp" field = token never expires!
    token = jwt.encode(     #jwt.encode is the function that creates the token from jose library
        {"sub": str(user_id), "email": email}, #payload of the token
        SECRET_KEY,     #secret key for JWT
        algorithm=ALGORITHM #Algorithm used for JWT
    )
    return token 

@app.post("/login")
def login(request: LoginRequest):
    for user in USERS:
        if (
            user["email"] == request.email and
            user["password"] == request.password
        ):
            token = create_token(user["id"], user["email"])
            return {
                "success": True,
                "id": user["id"],
                "email": user["email"],
                "token": token
            }

    raise HTTPException(status_code=400, detail="Wrong email or password")

    
# Run the app with: python -m uvicorn Backend.authentification.mainfourat:app --reload


class RegisterRequest(BaseModel):
    email: str
    password: str


@app.post("/register")
def register(request: RegisterRequest):
    #check if user already exists
    for user in USERS:
        if user["email"] == request.email:
            raise HTTPException(status_code=400, detail="User already exists")
    # Create a new user
    new_user = {
        "id": len(USERS) + 1,
        "email": request.email,
        "password": request.password
    }
    USERS.append(new_user)
    token = create_token(new_user["id"], new_user["email"])
    return {
        "success": True,
        "id": new_user["id"],
        "email": new_user["email"],
        "token": token
    }