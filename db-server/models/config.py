import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

db_username = os.getenv('DB_USERNAME', 'root')
db_password = os.getenv('DB_PASSWORD', 'admin')
db_host = os.getenv('DB_HOST', 'localhost')
db_database_name = os.getenv('DATABASE_NAME', 'mugo')
