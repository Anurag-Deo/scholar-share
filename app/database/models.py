from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    authors = Column(JSON)  # List of authors
    abstract = Column(Text)
    content = Column(Text)
    source_type = Column(String(50))  # pdf, url, text
    source_url = Column(String(500))
    complexity_level = Column(String(50))
    technical_terms = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class GeneratedContent(Base):
    __tablename__ = "generated_content"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, nullable=False)
    content_type = Column(String(50))  # blog, poster, social
    platform = Column(String(50))  # devto, linkedin, twitter, etc.
    title = Column(String(500))
    content = Column(Text)
    metadata = Column(JSON)
    is_published = Column(Boolean, default=False)
    published_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PublishingLog(Base):
    __tablename__ = "publishing_logs"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, nullable=False)
    platform = Column(String(50))
    status = Column(String(50))  # success, failed, pending
    response_data = Column(JSON)
    error_message = Column(Text)
    published_at = Column(DateTime(timezone=True), server_default=func.now())
