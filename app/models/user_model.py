from app.core.database import Base
from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    dob = Column(TIMESTAMP)
    first_name = Column(String(255))
    last_name = Column(String(255))
    username = Column(String(255), unique=True)
    password = Column(String(255))
    picture = Column(String(255))
    location = Column(String(255))
    email = Column(String(255), unique=True)
    phone = Column(String(255), unique=True)
    name_picture_firebase = Column(String(255))
    activated = Column(Boolean)
    activate_code = Column(String(255))


    # relationships
    # posts = relationship('Post')
    # groups = relationship('Group')
