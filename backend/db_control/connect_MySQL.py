from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

# データベース接続情報
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_SSL_CA = os.getenv("DB_SSL_CA")

# デバッグ用接続情報表示
print("[DB DEBUG]", DB_USER, DB_HOST, DB_NAME, DB_SSL_CA)

# MySQLのURL構築
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemyエンジン作成（Azure MySQL対応）
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "ssl": {
            "ca": DB_SSL_CA,
            "check_hostname": False
        }
    },
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=True
)