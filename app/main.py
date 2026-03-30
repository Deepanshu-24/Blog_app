from fastapi import FastAPI
from .models import Base
from .database import engine
from .routers import auth,admin,users,posts,likes,comments
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}


app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(likes.router)
app.include_router(comments.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://blottr.vercel.app",  
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)