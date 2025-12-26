from fastapi import FastAPI, HTTPException, Depends #fastapi tools and error handling
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials #security tools for handling bearer tokens
from pydantic import BaseModel #validation of the data (password and email)
from jose import jwt, JWTError #JWT creation and verification
from datetime import datetime, timedelta
from jose.exceptions import ExpiredSignatureError #exception for expired tokens
from passlib.context import CryptContext #password hashing


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

def create_token(user_id: int, email: str):
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=1) 
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/login")
def login(request: LoginRequest):
    for user in USERS:
        if (
            user["email"] == request.email and
            verify_password(request.password, user["password"])
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
        "password": hash_password(request.password) #hash the password before storing
    }
    USERS.append(new_user)
    token = create_token(new_user["id"], new_user["email"])
    return {
        "success": True,
        "id": new_user["id"],
        "email": new_user["email"],
        "token": token
    }

security=HTTPBearer() #instance of HTTPBearer for security
def get_current_user(credentials: HTTPAuthorizationCredentials=Depends(security)):
    token = credentials.credentials
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        email = payload.get("email")
        if user_id is None or email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"id": user_id, "email": email}
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
@app.get("/me") #protected route to get current user profile
def read_profile(current_user: dict = Depends(get_current_user)): #access current user data from the token
    return {
        "success": True,
        "user": current_user
    }

#password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
