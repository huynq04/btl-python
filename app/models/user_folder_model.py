from app.core.database import Base
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship


class User_Folder(Base):
    __tablename__ = 'user_folder'

    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    folder_id = Column(Integer, ForeignKey('folder.id'), primary_key=True)

    # relationships
    author = relationship('User')
    folder = relationship('Folder', lazy='joined', back_populates='user_folder')



