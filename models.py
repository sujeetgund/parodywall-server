import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    alias = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Admin(Base):
    __tablename__ = "admins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Pin(Base):
    __tablename__ = "pins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    type = Column(String, nullable=False)  # 'text', 'image', 'both'
    text_content = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    bg_color = Column(String, nullable=True)  # hex value, e.g. '#f6f6f3'
    categories = Column(ARRAY(String), nullable=False, server_default="{}")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class PinLike(Base):
    __tablename__ = "pin_likes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pin_id = Column(UUID(as_uuid=True), ForeignKey("pins.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("pin_id", "user_id", name="uq_pin_like"),)


class PinSave(Base):
    __tablename__ = "pin_saves"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pin_id = Column(UUID(as_uuid=True), ForeignKey("pins.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("pin_id", "user_id", name="uq_pin_save"),)


class PinReport(Base):
    __tablename__ = "pin_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pin_id = Column(UUID(as_uuid=True), ForeignKey("pins.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("pin_id", "user_id", name="uq_pin_report"),)
