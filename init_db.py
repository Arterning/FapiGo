"""
数据库初始化脚本
用于创建数据库表结构
"""
from app.core.database import Base, engine
from app.models.user import User
from app.models.book import Book
from app.models.book_image import BookImage


def init_db():
    """创建所有数据库表"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    init_db()
