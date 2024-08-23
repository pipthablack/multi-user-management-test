from django.urls import path
from .views import (
    TaskListCreateView,
    TaskDetailView,
    TaskListView,
    AddTagsToTaskView,
    CommentListCreateView,
    CommentDetailView
)

urlpatterns = [
    # Task Management URLs
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),

    # Tagging System URLs
    path('tag/<int:pk>/', AddTagsToTaskView.as_view(), name='tag-list-create'),
    path('task-tags/', TaskListView.as_view(), name='task-tag-list-create'),

    # Commenting System URLs
    path('tasks/<int:task_id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
]
