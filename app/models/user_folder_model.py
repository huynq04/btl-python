from app.core.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship


class User_Folder(Base):
    __tablename__ = 'user_folder'

    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    folder_id = Column(Integer, ForeignKey('folder.id'), primary_key=True)

    # relationships
    author = relationship('User')
    folder = relationship('Folder')



