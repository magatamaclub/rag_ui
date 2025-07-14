
from sqlalchemy import Column, Integer, String
from .database import Base

class DifyConfig(Base):
    __tablename__ = "dify_configs"

    id = Column(Integer, primary_key=True, index=True)
    api_url = Column(String, unique=True, index=True)
    api_key = Column(String)
