import uuid

from app.core.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, text, TIMESTAMP
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy import String

class Document(Base):
    __tablename__ = 'document'

    id = Column(Integer, primary_key=True, autoincrement=True)
    create_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    firebase_id = Column(text)
    name = Column(String)
    folder = Column(String, ForeignKey('folder.id'))
    slug = Column(String, unique=True)
    # relationships
    # creator = relationship('User')
    # group = relationship('Group')
    # comments = relationship('Comment')
