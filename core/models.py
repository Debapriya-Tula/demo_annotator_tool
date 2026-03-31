from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('company', 'Company'),
        ('annotator', 'Annotator'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='annotator')

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'

    def is_company(self):
        return self.role == 'company'

    def is_annotator(self):
        return self.role == 'annotator'


class Task(models.Model):
    FILE_TYPE_CHOICES = [
        ('image', 'Image'),
        ('pdf', 'PDF'),
    ]
    ANSWER_TYPE_CHOICES = [
        ('yes_no', 'Yes/No'),
        ('free_text', 'Free Text'),
    ]

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks',
        limit_choices_to={'role': 'company'},
    )
    file_url = models.URLField(max_length=500)
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    question = models.TextField()
    answer_type = models.CharField(max_length=20, choices=ANSWER_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return f'Task #{self.pk} by {self.uploaded_by.username}'


class Annotation(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='annotations')
    annotator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='annotations',
        limit_choices_to={'role': 'annotator'},
    )
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Annotation'
        verbose_name_plural = 'Annotations'
        # One annotator can only annotate a task once
        unique_together = [('task', 'annotator')]

    def __str__(self):
        return f'Annotation by {self.annotator.username} on Task #{self.task.pk}'
