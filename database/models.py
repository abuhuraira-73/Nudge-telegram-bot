from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, BigInteger
from sqlalchemy.sql import func
from database.db import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True) # Telegram User ID
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    timezone = Column(String, default="UTC")
    calendar_token = Column(String, nullable=True) # Stores JSON token data
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"))
    message = Column(String, nullable=False)
    remind_at = Column(DateTime(timezone=True), nullable=False)
    priority = Column(String, default="normal")
    is_done = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    notification_sent = Column(Boolean, default=False)
