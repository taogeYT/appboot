# Register your schema here.
from typing import Optional

from appboot.filters import ContainsField, EqField
from appboot.params import QuerySchema
from appboot.schema import ModelSchema
from polls.models import Choice, Question


class QuestionQuerySchema(QuerySchema):
    ids: Optional[list[int]] = EqField(None, alias='pk', columns='id')
    question_text: Optional[str] = ContainsField(None)


class QuestionSchema(ModelSchema):
    class Meta:
        model = Question
        fields = ('id', 'question_text', 'pub_date', 'created_at')
        read_only_fields = ('id', 'created_at')


class ChoiceSchema(ModelSchema):
    class Meta:
        model = Choice
