from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_CREDENCIALES = os.getenv("MONGO_CREDENCIALES")

db_client = MongoClient(MONGO_CREDENCIALES).test

metadata_collection = db_client["app_metadata"]