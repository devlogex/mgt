from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Case, When, IntegerField

class Todo(models.Model):
    # Priority choices
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    # Status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    category = models.CharField(max_length=50, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todos', null=True)
    position = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title
        
    class Meta:
        verbose_name = 'Todo'
        verbose_name_plural = 'Todos'
        ordering = [
            Case(
                When(status='in_progress', then=1),
                When(status='pending', then=2),
                When(status='completed', then=3),
                default=4,
                output_field=IntegerField(),
            ),
            Case(
                When(priority='high', then=1),
                When(priority='medium', then=2),
                When(priority='low', then=3),
                default=4,
                output_field=IntegerField(),
            ),
            'position'
        ]
