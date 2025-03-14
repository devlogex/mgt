from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Case, When, IntegerField
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import Group
from django.contrib.auth import logout
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Todo
from .forms import TodoForm

# Authentication Views
class CustomLoginView(LoginView):
    template_name = 'todo/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('todo:list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Login successful!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)

def logout_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'You have been logged out.')
        logout(request)
    return redirect('todo:login')

# Check if user is in customer group
def is_customer(user):
    return user.groups.filter(name='customer').exists() or user.is_superuser

# Create your views here.
class TodoListView(LoginRequiredMixin, ListView):
    model = Todo
    template_name = 'todo/todo_list.html'
    context_object_name = 'todos'
    login_url = reverse_lazy('todo:login')
    
    def get_queryset(self):
        queryset = Todo.objects.filter(user=self.request.user)
        
        # Filter by status if provided in the URL
        status_filter = self.request.GET.get('status')
        if status_filter in ['pending', 'in_progress', 'completed']:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range if provided in the URL
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if start_date and end_date:
            try:
                # Parse the date strings into datetime objects
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                # Add one day to end_date to include the end date in the results
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date() + timedelta(days=1)
                queryset = queryset.filter(updated_date__date__gte=start_date, 
                                          updated_date__date__lt=end_date)
            except ValueError:
                # If date parsing fails, ignore the filter
                pass
        
        # Use the model's default ordering (status, priority, position)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_todos = Todo.objects.filter(user=self.request.user)
        context['pending_count'] = user_todos.filter(status='pending').count()
        context['in_progress_count'] = user_todos.filter(status='in_progress').count()
        context['completed_count'] = user_todos.filter(status='completed').count()
        
        # Add the current status filter to the context
        context['current_status'] = self.request.GET.get('status', '')
        
        # Add the custom date range to the context
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        
        # Add the date label to the context
        context['date_label'] = self.request.GET.get('date_label', '')
        
        return context

class TodoCreateView(LoginRequiredMixin, CreateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todo/todo_form.html'
    success_url = reverse_lazy('todo:list')
    login_url = reverse_lazy('todo:login')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        # Set the position to be after the last task
        last_position = Todo.objects.filter(user=self.request.user).order_by('-position').first()
        if last_position:
            form.instance.position = last_position.position + 1
        else:
            form.instance.position = 1
        messages.success(self.request, 'Task created successfully!')
        return super().form_valid(form)

class TodoUpdateView(LoginRequiredMixin, UpdateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todo/todo_form.html'
    success_url = reverse_lazy('todo:list')
    login_url = reverse_lazy('todo:login')
    
    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            messages.error(self.request, "You don't have permission to modify this task.")
            return None
        return obj
    
    def form_valid(self, form):
        messages.success(self.request, 'Task updated successfully!')
        return super().form_valid(form)

class TodoDeleteView(LoginRequiredMixin, DeleteView):
    model = Todo
    template_name = 'todo/todo_confirm_delete.html'
    success_url = reverse_lazy('todo:list')
    login_url = reverse_lazy('todo:login')
    
    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            messages.error(self.request, "You don't have permission to delete this task.")
            return None
        return obj
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Task deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required(login_url=reverse_lazy('todo:login'))
def change_status(request, pk, status):
    # Get the task or return 404
    todo = get_object_or_404(Todo, pk=pk)
    
    # Check ownership - only allow if the task belongs to the user
    if todo.user != request.user:
        messages.error(request, "You don't have permission to modify this task.")
        return redirect('todo:list')
    
    # Check if user has permission to change task status
    if not is_customer(request.user):
        messages.error(request, "You need to be a customer to change task status.")
        return redirect('todo:list')
    
    # Now that we've verified both ownership and permission, update the status
    todo.status = status
    todo.save()
    messages.success(request, f'Task status changed to {status.replace("_", " ").title()}!')
    return redirect('todo:list')

@login_required(login_url=reverse_lazy('todo:login'))
def reorder_tasks(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Get the task IDs in their new order
        task_ids = request.POST.getlist('task_ids[]')
        status_filter = request.POST.get('status', '')
        
        # Validate all tasks belong to the current user
        tasks = Todo.objects.filter(id__in=task_ids, user=request.user)
        if len(tasks) != len(task_ids):
            return JsonResponse({'status': 'error', 'message': 'Unauthorized task access'}, status=403)
        
        # Update positions
        for i, task_id in enumerate(task_ids):
            task = Todo.objects.get(id=task_id)
            task.position = i + 1
            task.save()
            
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
