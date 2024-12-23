# Create your models here.
from datetime import datetime

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from appboot import Schema, models
from appboot.models import PydanticType


class Extra(Schema):
    create_by: int
    update_by: int


class Question(
    models.DeletedAtMixin, models.TimestampMixin, models.TableNameMixin, models.Model
):
    question_text: Mapped[str]
    pub_date: Mapped[datetime]
    extra: Mapped[Extra] = mapped_column(PydanticType(Extra))
    choices: Mapped[list['Choice']] = relationship()


class Choice(models.TableNameMixin, models.Model):
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey('question.id'))
    choice_text: Mapped[str]
    votes: Mapped[int] = mapped_column(default=0)
