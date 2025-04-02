from todo.views.auth import CustomLoginView, logout_view, is_customer
from todo.views.todo import (
    TodoListView, TodoCreateView, TodoUpdateView, TodoDeleteView,
    change_status, reorder_tasks
)
from todo.views.goal import (
    GoalListView, GoalDetailView, GoalCreateView, GoalUpdateView, GoalDeleteView,
    add_task_to_goal, task_assign_goal
)

__all__ = [
    'CustomLoginView', 'logout_view', 'is_customer',
    'TodoListView', 'TodoCreateView', 'TodoUpdateView', 'TodoDeleteView',
    'change_status', 'reorder_tasks',
    'GoalListView', 'GoalDetailView', 'GoalCreateView', 'GoalUpdateView', 'GoalDeleteView',
    'add_task_to_goal', 'task_assign_goal'
]