from rest_framework import serializers
from ..models import Task, TaskStatus


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model.
    Handles serialization/deserialization of Task instances with validation.
    """
    
    class Meta:
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_title(self, value):
        """
        Validate that title is not empty or whitespace-only.
        Also validates max length of 255 characters.
        """
        if value is None or value.strip() == '':
            raise serializers.ValidationError("Title cannot be empty or whitespace-only.")
        
        if len(value) > 255:
            raise serializers.ValidationError("Title cannot exceed 255 characters.")
        
        return value
    
    def validate_status(self, value):
        """
        Validate that status is one of the allowed TaskStatus choices.
        """
        if value not in TaskStatus.values:
            valid_statuses = ', '.join(TaskStatus.values)
            raise serializers.ValidationError(
                f"Invalid status. Must be one of: {valid_statuses}"
            )
        return value
    
    def validate_description(self, value):
        """
        Description is optional. If provided, strip whitespace.
        """
        if value is not None:
            return value.strip()
        return value
