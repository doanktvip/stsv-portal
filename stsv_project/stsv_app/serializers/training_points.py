from rest_framework import serializers
from stsv_app.models.training_points import TrainingCriterion

class TrainingCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingCriterion
        fields = ['id', 'code', 'name', 'max_points', 'parent']
