from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Group, Student, AttendanceRecord, ScheduleTask
from .serializers import GroupSerializer, StudentSerializer, AttendanceRecordSerializer, ScheduleTaskSerializer


class GetAttendanceByGroup(APIView):
    def get(self, request, group_id, format=None):
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)

        attendance_records = AttendanceRecord.objects.filter(group=group)
        serializer = AttendanceRecordSerializer(attendance_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateAttendance(APIView):
    def post(self, request, format=None):
        student_id = request.data.get("student_id")
        group_id = request.data.get("group_id")

        # Проверяем существование студента
        try:
            student = Student.objects.get(student_id=student_id)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем существование группы
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)

        # Создаем запись о присутствии
        attendance_record = AttendanceRecord(group=group, student=student)
        attendance_record.save()

        serializer = AttendanceRecordSerializer(attendance_record)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
'''

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

'''
# Получение всех групп
class GetGroups(APIView):
    def get(self, request):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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


class GetStudentById(APIView):
    def get(self, request, student_id):
        try:
            student = Student.objects.get(student_id=student_id)
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


class GetStudentsByGroupAndPatchGroup(APIView):
    def get(self, request, group_id, format=None):
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)

        # Получаем всех студентов, принадлежащих к указанной группе
        students = Student.objects.filter(group=group)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, group_id, format=None):
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)

        # Обновляем поля chat и thread_id
        chat_id = request.data.get('chat')
        thread_id = request.data.get('thread_id')

        if chat_id is not None:
            group.chat = chat_id
        if thread_id is not None:
            group.thread_id = thread_id

        group.save()

        # Возвращаем обновленные данные группы
        serializer = GroupSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClearAttendance(APIView):
    def post(self, request, group_id, format=None):
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)

        # Удаляем все записи о присутствии для группы
        deleted_count, _ = AttendanceRecord.objects.filter(group=group).delete()

        return Response({"message": f"Удалено {deleted_count} записей о присутствии."}, status=status.HTTP_200_OK)


class ScheduleTaskViewSet(viewsets.ModelViewSet):
    queryset = ScheduleTask.objects.all()
    serializer_class = ScheduleTaskSerializer