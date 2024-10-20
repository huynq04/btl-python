import uuid

from app.core.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship


class Folder(Base):
    __tablename__ = 'folder'

    id = Column(Integer, primary_key=True, autoincrement=True)
    create_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    name = Column(String)
    view = Column(Integer)
    author = Column(String, ForeignKey('user.id'))
    slug = Column(String)
    star = Column(Integer)
