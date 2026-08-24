from urllib.parse import quote_plus

class Config:
    MYSQL_USER = "root"
    MYSQL_PASSWORD = quote_plus("24pd18")
    MYSQL_HOST = "localhost"
    MYSQL_PORT = 3307
    MYSQL_DB = "tasklink_db"

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "tasklink_secret_2024"