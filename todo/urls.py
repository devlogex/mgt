from django.urls import path
from . import views

app_name = 'todo'

urlpatterns = [
    path('', views.TodoListView.as_view(), name='list'),
    path('create/', views.TodoCreateView.as_view(), name='create'),
    path('update/<int:pk>/', views.TodoUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', views.TodoDeleteView.as_view(), name='delete'),
    path('change-status/<int:pk>/<str:status>/', views.change_status, name='change_status'),
    path('reorder-tasks/', views.reorder_tasks, name='reorder_tasks'),
    
    # Authentication URLs
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
] 