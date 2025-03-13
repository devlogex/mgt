from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Case, When, IntegerField
from .models import Todo
from .forms import TodoForm

# Create your views here.

class TodoListView(ListView):
    model = Todo
    template_name = 'todo/todo_list.html'
    context_object_name = 'todos'
    
    def get_queryset(self):
        queryset = Todo.objects.all()
        
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
        context['pending_count'] = Todo.objects.filter(status='pending').count()
        context['in_progress_count'] = Todo.objects.filter(status='in_progress').count()
        context['completed_count'] = Todo.objects.filter(status='completed').count()
        
        # Add the current status filter to the context
        context['current_status'] = self.request.GET.get('status', '')
        
        return context

class TodoCreateView(CreateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todo/todo_form.html'
    success_url = reverse_lazy('todo:list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Task created successfully!')
        return super().form_valid(form)

class TodoUpdateView(UpdateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todo/todo_form.html'
    success_url = reverse_lazy('todo:list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Task updated successfully!')
        return super().form_valid(form)

class TodoDeleteView(DeleteView):
    model = Todo
    template_name = 'todo/todo_confirm_delete.html'
    success_url = reverse_lazy('todo:list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Task deleted successfully!')
        return super().delete(request, *args, **kwargs)

def change_status(request, pk, status):
    todo = get_object_or_404(Todo, pk=pk)
    todo.status = status
    todo.save()
    messages.success(request, f'Task status changed to {status.replace("_", " ").title()}!')
    return redirect('todo:list')
