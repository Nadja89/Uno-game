import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID

from db.database import Base


class GameModel(Base):
    __tablename__ = "games"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state = Column(JSONB, nullable=False)
    finished = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )