from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Group, Student
from .serializers import GroupSerializer, StudentSerializer


class UpdateGroup(APIView):
    def patch(self, request, group_id):
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = GroupSerializer(group, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Получение всех групп
class GetGroups(APIView):
    def get(self, request):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Создание новой группы
class CreateGroup(APIView):
    def post(self, request):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Получение студента по Telegram ID
class GetStudentByTelegramId(APIView):
    def get(self, request, telegram_id):
        try:
            student = Student.objects.get(telegram_id=telegram_id)
            serializer = StudentSerializer(student)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

# Проверка авторизации студента
class IsAuthorizedStudent(APIView):
    def get(self, request, telegram_id):
        is_authorized = Student.objects.filter(telegram_id=telegram_id, active=True).exists()
        return Response({"is_authorized": is_authorized}, status=status.HTTP_200_OK)

# Активация студента
class ActivateStudent(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        telegram_id = request.data.get('telegram_id')
        group_id = request.data.get('group_id')  # Добавляем возможность назначения группы

        try:
            student = Student.objects.get(phone=phone, active=False)
            student.telegram_id = telegram_id
            student.active = True
            if group_id:
                student.group = Group.objects.get(id=group_id)  # Присваиваем группу
            student.save()
            return Response({"message": "Student activated successfully"}, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response({"error": "Inactive student with given phone not found"}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)