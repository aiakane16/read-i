from rest_framework import serializers
from apps.models import Modules, Question, User_Module_Answer, Users, Choice, Answer, UserCompletedModules

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
      model = Answer
      fields = '__all__'
  
class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id','text','question']

class QuestionSerializer(serializers.ModelSerializer):
  choices = ChoiceSerializer(many=True, read_only=True)
  # answer = AnswerSerializer(read_only=True)

  class Meta:
    model = Question
    fields = '__all__'

class ModulesSerializer(serializers.ModelSerializer):
  questions_per_module = QuestionSerializer(many=True, read_only=True)
  isLock = serializers.SerializerMethodField()
  class Meta:
    model = Modules
    fields = '__all__'
  def get_isLock(self, obj):
      user = self.context['request'].user
      return not is_module_unlocked(user, obj)

class UserModuleAsnwerSerializer(serializers.ModelSerializer):
  class Meta:
    model = User_Module_Answer
    fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = Users
    fields = '__all__'


# Define this function if not already present
def is_module_unlocked(user, module):
    if module.difficulty == "Easy":
        return True

    previous_level = get_previous_difficulty(module.difficulty)
    return UserCompletedModules.objects.filter(
        user=user, module__difficulty=previous_level, module__category=module.category
    ).exists()

def get_previous_difficulty(current_difficulty):
    levels = ["Easy", "Medium", "Hard"]
    try:
        index = levels.index(current_difficulty)
        return levels[index - 1] if index > 0 else None
    except ValueError:
        return None
