from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


class Goal(models.Model):
    """A goal represents a larger objective that may contain multiple tasks."""
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    color = models.CharField(max_length=20, default="#3498db")  # Default blue color
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('todo:goal_detail', args=[str(self.id)])
    
    def task_count(self):
        """Returns the total number of tasks in this goal."""
        return self.tasks.count()
    
    def completed_task_count(self):
        """Returns the number of completed tasks in this goal."""
        return self.tasks.filter(status='completed').count()
    
    def progress_percentage(self):
        """Calculate the progress percentage based on completed tasks."""
        total = self.task_count()
        if total == 0:
            return 0
        return int((self.completed_task_count() / total) * 100)
    
    def status(self):
        """Determine the status of the goal based on task completion."""
        total = self.task_count()
        completed = self.completed_task_count()
        
        if total == 0:
            return 'not_started'
        elif completed == 0:
            return 'not_started'
        elif completed == total:
            return 'completed'
        else:
            return 'in_progress'
    
    def status_display(self):
        """Return a user-friendly status display."""
        status_map = {
            'not_started': 'Not Started',
            'in_progress': 'In Progress',
            'completed': 'Completed'
        }
        return status_map.get(self.status(), 'In Progress')
    
    def days_remaining(self):
        """Calculate the number of days remaining until the goal end date."""
        today = timezone.now().date()
        if self.end_date < today:
            return 0
        return (self.end_date - today).days
    
    def is_overdue(self):
        """Check if the goal is overdue."""
        return self.end_date < timezone.now().date() and self.status() != 'completed'
    
    class Meta:
        ordering = ['end_date', '-created_date'] 