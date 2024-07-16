# Register your schema here.
from appboot import ModelSchema
from polls.models import Choice, Question


class QuestionSchema(ModelSchema):
    class Meta:
        model = Question


class ChoiceSchema(ModelSchema):
    class Meta:
        model = Choice
