# Register your schema here.
from typing import Optional

from appboot import ModelSchema, PaginationQuerySchema, filters
from polls.models import Choice, Question


class QuestionQuerySchema(PaginationQuerySchema):
    ids: Optional[list[int]] = filters.EqField(None, alias='pk', columns='id')
    question_text: Optional[str] = filters.ContainsField(None)


class QuestionSchema(ModelSchema):
    choices: Optional[list['ChoiceSchema']] = None

    class Meta:
        model = Question
        fields = ('id', 'question_text', 'pub_date')


class ChoiceSchema(ModelSchema):
    class Meta:
        model = Choice
        exclude = ('updated_at', 'created_at')
