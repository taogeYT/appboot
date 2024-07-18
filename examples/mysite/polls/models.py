# Create your models here.
from datetime import datetime

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from appboot import models


class Question(models.TimestampMixin, models.Model):
    question_text: Mapped[str]
    pub_date: Mapped[datetime]


class Choice(models.Model):
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("question.id"))
    choice_text: Mapped[str]
    votes: Mapped[int] = mapped_column(Integer, default=0)
