from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

#Base de datos local
#db_client = MongoClient()

MONGO_CREDENCIALES = os.getenv("MONGO_CREDENCIALES")
#Base de datos remota
db_client = MongoClient(MONGO_CREDENCIALES).test