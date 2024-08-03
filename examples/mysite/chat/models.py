# Create your models here.

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import mapped_column, relationship

from appboot import models, timezone


class User(models.TimestampMixin, models.Model):
    username = mapped_column(String(50), unique=True, nullable=False)
    password = mapped_column(String(128), nullable=False)


class Message(models.TimestampMixin, models.Model):
    user_id = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    text = mapped_column(Text, nullable=False)
    timestamp = mapped_column(DateTime(timezone=True), default=timezone.now)
    user = relationship('User')
