from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class ProviderOffer(Base):
    __tablename__ = "provider_offers"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String, index=True)
    offer_id = Column(String, index=True)
    raw_data = Column(JSON)
    normalized_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Normalized fields for comparison
    download_speed = Column(Float)
    upload_speed = Column(Float)
    price = Column(Float)
    contract_length = Column(Integer)  # in months
    setup_fee = Column(Float)
    cancellation_fee = Column(Float)
    
    # Cache metadata
    cache_expires_at = Column(DateTime)
    last_fetched = Column(DateTime)
    fetch_status = Column(String)  # success, error, pending

class APIRequestLog(Base):
    __tablename__ = "api_request_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String, index=True)
    endpoint = Column(String)
    request_time = Column(DateTime, default=datetime.utcnow)
    response_time = Column(Float)  # in seconds
    status_code = Column(Integer)
    error_message = Column(String, nullable=True)
    success = Column(Boolean)

class CircuitBreakerState(Base):
    __tablename__ = "circuit_breaker_states"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String, unique=True, index=True)
    failure_count = Column(Integer, default=0)
    last_failure_time = Column(DateTime, nullable=True)
    state = Column(String)  # closed, open, half-open
    last_state_change = Column(DateTime, default=datetime.utcnow) 