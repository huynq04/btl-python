from app.core.database import Base
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP


class Otp(Base):
    __tablename__ = 'otp'

    id = Column(Integer, primary_key=True, autoincrement=True)
    otp_code=Column(String(255))
    expiry_time=Column(TIMESTAMP)
    user_id=Column(Integer,ForeignKey('user.id'))

    user=relationship('User')