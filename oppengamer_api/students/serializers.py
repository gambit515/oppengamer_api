from rest_framework import serializers
from .models import Group, Student

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'  # Все поля модели Group


class StudentSerializer(serializers.ModelSerializer):
    group = GroupSerializer(read_only=True)  # Включаем информацию о группе в сериализацию

    class Meta:
        model = Student
        fields = '__all__'  # Все поля модели Student