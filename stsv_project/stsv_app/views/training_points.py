from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from stsv_app.models.training_points import TrainingCriterion
from stsv_app.serializers.training_points import TrainingCriterionSerializer

class TrainingCriterionViewSet(viewsets.ModelViewSet):
    queryset = TrainingCriterion.objects.all()
    serializer_class = TrainingCriterionSerializer
    permission_classes = [IsAuthenticated] # Adjust as needed (e.g. IsAdminUser)
