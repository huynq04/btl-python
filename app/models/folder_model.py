from app.core.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship


class Folder(Base):
    __tablename__ = 'folder'

    id = Column(Integer, primary_key=True, autoincrement=True)
    create_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    name = Column(String(255))
    view = Column(Integer, default=0)
    author_id = Column(Integer, ForeignKey('user.id'))
    slug = Column(String(255))
    star = Column(Integer, default=0)

    # relationships
    author = relationship('User')
    documents = relationship('Document', back_populates='folder', cascade="all, delete")

