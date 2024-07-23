# Register your schema here.
from appboot.schema import ModelSchema
from polls.models import Choice, Question


class QuestionSchema(ModelSchema):
    class Meta:
        model = Question
        read_only_fields = ('id', 'created_at', 'updated_at')


class ChoiceSchema(ModelSchema):
    class Meta:
        model = Choice
