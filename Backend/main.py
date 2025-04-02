import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Importa el middleware CORS
from routers import  users
from fastapi.staticfiles import StaticFiles

app = FastAPI()

origins = [
    "http://localhost:5173",  # Reemplaza 3000 con el puerto correcto de React
    "http://localhost",       # Incluye localhost sin puerto
    "http://127.0.0.1:5173", # Incluye 127.0.0.1 por si acaso
    "https://notastartupanymore-front.onrender.com/"
    # Puedes añadir otros orígenes aquí si es necesario (ej: tu dominio en producción)
]

app.add_middleware(  # Añade el middleware CORS
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Si necesitas cookies o autenticación
    allow_methods=["*"],      # Permite todos los métodos
    allow_headers=["*"],      # Permite todos los encabezados
)

# Routers (DEBEN ir DESPUÉS del middleware CORS)
app.include_router(users.router)

# Static
#app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return "Hola FastAPI"

@app.get("/url")
async def url():
    return { "url_curso":"https://mouredev.com/python" }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render asigna un puerto, pero 8000 es el default en local
    uvicorn.run(app, host="0.0.0.0", port=port)