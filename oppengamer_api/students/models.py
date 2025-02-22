from django.db import models

class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Название группы
    description = models.TextField(blank=True, null=True)  # Описание группы

    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    patronymic = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=20, unique=True)
    student_id = models.AutoField(primary_key=True)  # ID студента
    telegram_id = models.BigIntegerField(null=True, blank=True)
    active = models.BooleanField(default=False)
    rights = models.CharField(max_length=50, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')

    def __str__(self):
        return f"{self.surname} {self.name}"

    @property
    def full_name(self):
        return f"{self.surname} {self.name} {self.patronymic or ''}".lower()