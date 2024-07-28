# Register your schema here.
from typing import Optional

from appboot.filters import ContainsField, EqField
from appboot.params import QuerySchema
from appboot.schema import ModelSchema
from polls.models import Choice, Question


class QuestionQuerySchema(QuerySchema):
    ids: Optional[list[int]] = EqField(None, column_name='id')
    question_text: Optional[str] = ContainsField(None)


class QuestionSchema(ModelSchema):
    class Meta:
        model = Question
        read_only_fields = ('id', 'created_at', 'updated_at')


class ChoiceSchema(ModelSchema):
    class Meta:
        model = Choice
