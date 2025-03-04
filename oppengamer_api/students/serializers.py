from rest_framework import serializers
from .models import *


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'  # Все поля модели Group


class StudentSerializer(serializers.ModelSerializer):
    group = GroupSerializer(read_only=True)  # Включаем информацию о группе в сериализацию

    class Meta:
        model = Student
        fields = '__all__'  # Все поля модели Student


class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = ['id', 'group', 'student', 'timestamp']


class ScheduleTaskSerializer(serializers.ModelSerializer):
    thread_id = serializers.CharField(source='group.thread_id', allow_null=True, required=False)
    class Meta:
        model = ScheduleTask
        fields = ['id', 'day', 'time', 'action', 'chat_id', 'group', 'thread_id']