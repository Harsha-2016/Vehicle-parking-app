# backend/models/db_setup.py
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from flask_cors import CORS

db = SQLAlchemy()
jwt = JWTManager()
cache = Cache(config={'CACHE_TYPE': 'RedisCache', 'CACHE_REDIS_URL': 'redis://localhost:6379/0'})
cors = CORS()

