# Register your schema here.
from typing import Optional

from appboot import ModelSchema, QuerySchema, filters
from polls.models import Choice, Question


class QuestionQuerySchema(QuerySchema):
    ids: Optional[list[int]] = filters.EqField(alias='pk', columns='id')
    question_text: Optional[str] = filters.ContainsField()


class QuestionSchema(ModelSchema):
    choices: Optional[list['ChoiceSchema']] = None

    class Meta:
        model = Question
        fields = ('id', 'question_text', 'pub_date')


class ChoiceSchema(ModelSchema):
    class Meta:
        model = Choice
        exclude = ('updated_at', 'created_at')
