from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import Mapped

from appboot import Model


class Question(Model):
    __tablename__ = "question"
    question_text: Mapped[str]
    pub_date: Mapped[datetime]


class Choice(Model):
    __tablename__ = "choice"
    question_id: Mapped[int] = Column(Integer, ForeignKey("question.id"))
    choice_text: Mapped[str]
    votes: Mapped[int] = Column(Integer, default=0)
