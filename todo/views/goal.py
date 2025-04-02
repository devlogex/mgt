from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404

from todo.models import Goal, Todo
from todo.forms import GoalForm, TodoForm


class GoalListView(LoginRequiredMixin, ListView):
    model = Goal
    template_name = 'todo/goal_list.html'
    context_object_name = 'goals'
    
    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get counts by status
        user_goals = Goal.objects.filter(user=self.request.user)
        
        # Add progress statistics
        not_started = 0
        in_progress = 0
        completed = 0
        
        for goal in user_goals:
            status = goal.status()
            if status == 'not_started':
                not_started += 1
            elif status == 'in_progress':
                in_progress += 1
            elif status == 'completed':
                completed += 1
        
        context['not_started_count'] = not_started
        context['in_progress_count'] = in_progress
        context['completed_count'] = completed
        context['total_count'] = user_goals.count()
        
        return context


class GoalDetailView(LoginRequiredMixin, DetailView):
    model = Goal
    template_name = 'todo/goal_detail.html'
    context_object_name = 'goal'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Check if the goal belongs to the current user
        if obj.user != self.request.user:
            messages.error(self.request, "You don't have permission to view this goal.")
            raise Http404("Goal not found")
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the tasks for this goal
        context['tasks'] = self.object.tasks.all()
        return context


class GoalCreateView(LoginRequiredMixin, CreateView):
    model = Goal
    form_class = GoalForm
    template_name = 'todo/goal_form.html'
    success_url = reverse_lazy('todo:goal_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Goal created successfully!")
        return super().form_valid(form)


class GoalUpdateView(LoginRequiredMixin, UpdateView):
    model = Goal
    form_class = GoalForm
    template_name = 'todo/goal_form.html'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Check if the goal belongs to the current user
        if obj.user != self.request.user:
            messages.error(self.request, "You don't have permission to edit this goal.")
            raise Http404("Goal not found")
        return obj
    
    def get_success_url(self):
        return reverse_lazy('todo:goal_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, "Goal updated successfully!")
        return super().form_valid(form)


class GoalDeleteView(LoginRequiredMixin, DeleteView):
    model = Goal
    template_name = 'todo/goal_confirm_delete.html'
    success_url = reverse_lazy('todo:goal_list')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Check if the goal belongs to the current user
        if obj.user != self.request.user:
            messages.error(self.request, "You don't have permission to delete this goal.")
            raise Http404("Goal not found")
        return obj
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Goal deleted successfully!")
        return super().delete(request, *args, **kwargs)


@login_required
def add_task_to_goal(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    
    if request.method == 'POST':
        form = TodoForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.goal = goal
            task.save()
            messages.success(request, "Task added to goal successfully!")
            return redirect('todo:goal_detail', pk=goal.id)
    else:
        form = TodoForm(user=request.user, initial={'goal': goal})
    
    return render(request, 'todo/add_task_to_goal.html', {
        'form': form,
        'goal': goal
    })


@login_required
def task_assign_goal(request, task_id):
    task = get_object_or_404(Todo, id=task_id, user=request.user)
    
    if request.method == 'POST':
        goal_id = request.POST.get('goal_id')
        if goal_id:
            goal = get_object_or_404(Goal, id=goal_id, user=request.user)
            task.goal = goal
            task.save()
            messages.success(request, f"Task assigned to goal: {goal.title}")
        else:
            task.goal = None
            task.save()
            messages.success(request, "Task removed from goal")
        
        # Redirect back to the referring page
        return redirect(request.META.get('HTTP_REFERER', 'todo:list'))
    
    # If not POST, show the form
    goals = Goal.objects.filter(user=request.user)
    return render(request, 'todo/task_assign_goal.html', {
        'task': task,
        'goals': goals
    }) 