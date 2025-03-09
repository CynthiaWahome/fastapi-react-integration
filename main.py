import uvicorn
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from backend.routers import auth
from backend.routers import user
from backend.core.config import CORS_ORIGINS  # Import settings from config

# Initialize the rate limiter before creating the FastAPI app
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(debug=True)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # Use the config value
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add a test route with rate limiting
@app.get("/", dependencies=[Depends(limiter.limit("10/minute"))])
async def root():
    return {"message": "API is working!"}

app.include_router(user.router)
app.include_router(auth.router, prefix="/auth")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)