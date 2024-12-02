from sqlalchemy import Column, Integer, ForeignKey, text, TIMESTAMP
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy import String


class Document(Base):
    __tablename__ = 'document'

    id = Column(Integer, primary_key=True, autoincrement=True)
    create_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    firebase_id = Column(String(255))
    name = Column(String(255))
    folder_id = Column(Integer, ForeignKey('folder.id'))

    # relationships
    folder = relationship('Folder', back_populates='documents')
