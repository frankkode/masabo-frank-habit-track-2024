
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Habit
from .serializers import HabitSerializer

class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    
    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        habit = self.get_object()
        habit.completions.create(completed_at=timezone.now())
        return Response({
            'status': 'success',
            'streak': habit.get_streak(),
            'completion_rate': habit.get_completion_rate()
        })
        
        