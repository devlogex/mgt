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
            
        # Custom ordering: Status (In Progress > Pending > Completed) and Priority (High > Medium > Low)
        return queryset.annotate(
            status_order=Case(
                When(status='in_progress', then=1),
                When(status='pending', then=2),
                When(status='completed', then=3),
                default=4,
                output_field=IntegerField(),
            ),
            priority_order=Case(
                When(priority='high', then=1),
                When(priority='medium', then=2),
                When(priority='low', then=3),
                default=4,
                output_field=IntegerField(),
            )
        ).order_by('status_order', 'priority_order')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_todos = Todo.objects.filter(user=self.request.user)
        context['pending_count'] = user_todos.filter(status='pending').count()
        context['in_progress_count'] = user_todos.filter(status='in_progress').count()
        context['completed_count'] = user_todos.filter(status='completed').count()
        
        # Add the current status filter to the context
        context['current_status'] = self.request.GET.get('status', '')
        
        return context

class TodoCreateView(LoginRequiredMixin, CreateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todo/todo_form.html'
    success_url = reverse_lazy('todo:list')
    login_url = reverse_lazy('todo:login')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
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
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Task deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required(login_url=reverse_lazy('todo:login'))
@user_passes_test(is_customer, login_url=reverse_lazy('todo:login'))
def change_status(request, pk, status):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    todo.status = status
    todo.save()
    messages.success(request, f'Task status changed to {status.replace("_", " ").title()}!')
    return redirect('todo:list')
