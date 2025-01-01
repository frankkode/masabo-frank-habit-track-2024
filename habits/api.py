from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Habit, HabitCompletion
from .serializers import HabitSerializer, HabitCompletionSerializer

class HabitViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = HabitSerializer

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        habit = self.get_object()
        completion = HabitCompletion.objects.create(
            habit=habit,
            completed_at=timezone.now()
        )
        return Response({'status': 'completed'})