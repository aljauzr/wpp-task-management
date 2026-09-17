from rest_framework import serializers
from ..models import Board
from .task_serializer import TaskSerializer


class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer for Board model.
    Handles serialization/deserialization of Board instances with nested tasks.
    """
    tasks = TaskSerializer(many=True, read_only=True)
    
    class Meta:
        model = Board
        fields = ['id', 'name', 'created_at', 'updated_at', 'tasks']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        """
        Validate that name is not empty or whitespace-only.
        """
        if value is None or value.strip() == '':
            raise serializers.ValidationError("Name cannot be empty or whitespace-only.")
        return value
