from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text
from sqlalchemy.dialects.mysql import LONGTEXT
from .database.connector import Base

import pytz
utc_plus_7 = pytz.timezone('Asia/Bangkok') 

class AnalyzeResult(Base):
    __tablename__ = 'AnalyzeResult'
    id = Column(String(255), primary_key=True, index=True)
    api_version = Column(String(255))
    file_name = Column(Text)
    file_size = Column(Integer)
    file_extension = Column(String(255))
    model = Column(String(255))
    output_data = Column(LONGTEXT)
    input_token = Column(Integer)
    output_token = Column(Integer)
    estimated_cost = Column(Float)
    created_at = Column(String(255), default=str(datetime.now(utc_plus_7)))
    updated_at = Column(String(255), default=str(datetime.now(utc_plus_7)), onupdate=str(datetime.now(utc_plus_7)))