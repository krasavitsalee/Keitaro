from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.database import Base


class CampaignRecord(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    country_code = Column(String, nullable=True)
    offer_id = Column(Integer, nullable=True)
    keitaro_campaign_id = Column(Integer, nullable=True, index=True)
    domain_id = Column(Integer, nullable=True)
    group_id = Column(Integer, nullable=True)
    traffic_source_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class OfferChangeLog(Base):
    __tablename__ = "offer_change_logs"
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    stream_id = Column(Integer, nullable=True)
    offer_id = Column(Integer, nullable=True)
    action = Column(String, nullable=False)  # add / remove
    created_at = Column(DateTime, default=datetime.utcnow)