# Create your models here.
from datetime import datetime

from sqlalchemy import ForeignKey, Integer

from appboot import models


class Question(models.Model):
    __tablename__ = "question"
    question_text: models.Mapped[str]
    pub_date: models.Mapped[datetime]


class Choice(models.Model):
    __tablename__ = "choice"
    question_id: models.Mapped[int] = models.Column(Integer, ForeignKey("question.id"))
    choice_text: models.Mapped[str]
    votes: models.Mapped[int] = models.Column(Integer, default=0)
