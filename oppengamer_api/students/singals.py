# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm
from django.contrib.auth.models import User
from .models import Student, ScheduleTask, Group

@receiver(post_save, sender=Student)
def assign_student_permissions(sender, instance, created, **kwargs):
    if created and instance.group:  # Если студент создан и связан с группой
        users_in_group = User.objects.filter(profile__group=instance.group)
        for user in users_in_group:
            assign_perm("view_student", user, instance)

@receiver(post_save, sender=ScheduleTask)
def assign_scheduletask_permissions(sender, instance, created, **kwargs):
    if created and instance.group:  # Если задача расписания создана и связана с группой
        users_in_group = User.objects.filter(profile__group=instance.group)
        for user in users_in_group:
            assign_perm("view_scheduletask", user, instance)