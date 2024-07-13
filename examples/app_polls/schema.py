from app_polls.models import Choice, Question
from appboot import ModelSchema


class QuestionSchema(ModelSchema):
    class Meta:
        model = Question


class ChoiceSchema(ModelSchema):
    class Meta:
        model = Choice
