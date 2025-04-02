from django.urls import path
from . import views

app_name = 'todo'

urlpatterns = [
    # Auth URLs
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Todo URLs
    path('', views.TodoListView.as_view(), name='list'),
    path('add/', views.TodoCreateView.as_view(), name='add'),
    path('update/<int:pk>/', views.TodoUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', views.TodoDeleteView.as_view(), name='delete'),
    path('change-status/<int:pk>/<str:status>/', views.change_status, name='change_status'),
    path('reorder-tasks/', views.reorder_tasks, name='reorder_tasks'),
    
    # Goal URLs
    path('goals/', views.GoalListView.as_view(), name='goal_list'),
    path('goals/add/', views.GoalCreateView.as_view(), name='goal_add'),
    path('goals/<int:pk>/', views.GoalDetailView.as_view(), name='goal_detail'),
    path('goals/update/<int:pk>/', views.GoalUpdateView.as_view(), name='goal_update'),
    path('goals/delete/<int:pk>/', views.GoalDeleteView.as_view(), name='goal_delete'),
    path('goals/<int:goal_id>/add-task/', views.add_task_to_goal, name='add_task_to_goal'),
    path('tasks/<int:task_id>/assign-goal/', views.task_assign_goal, name='task_assign_goal'),
] 