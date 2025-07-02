from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from routers import  users
from fastapi.staticfiles import StaticFiles

app = FastAPI()

origins = [
    "http://localhost:5173",  
    "http://localhost",       
    "http://127.0.0.1:5173", 
    "https://notastartupanymore-front.onrender.com"

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  
    allow_methods=["*"],     
    allow_headers=["*"],
)

app.include_router(users.router)


@app.get("/")
async def root():
    return "Hola NotAStartUpAnymore"

