from django_filters.rest_framework import filters
from rest_framework import generics, permissions, filters,status
from .models import Task, Tag, Comment
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.authentication import JWTAuthentication
from .pagination import TaskPagination
from .filters import TaskFilter 
from .serializers import *




class TaskListCreateView(generics.ListCreateAPIView):
    """
    This view handles listing and creating tasks.

    Attributes:
    queryset: The queryset of all tasks.
    serializer_class: The serializer class for tasks.
    authentication_classes: The authentication classes used for this view.
    permission_classes: The permission classes required for this view.
    filter_backends: The filter backends used for this view.
    filterset_class: The filterset class for filtering tasks.
    pagination_class: The pagination class for this view.

    Methods:
    get_queryset: Returns the queryset based on user permissions.
    perform_create: Creates a new task with the assigned user and creator.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [JWTAuthentication]  
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter
    pagination_class = TaskPagination 
     
    def get_queryset(self):
        if self.request.user.is_staff:
            return Task.objects.all()
        return Task.objects.filter(assigned_to=self.request.user)

    def perform_create(self, serializer):
        assigned_user_id = self.request.data.get('assigned_to')
        if assigned_user_id:
            assigned_user = User.objects.get(id=assigned_user_id)
            serializer.save(assigned_to=assigned_user, created_by=self.request.user)
        else:
            serializer.save(created_by=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    This view handles retrieving, updating, and deleting a single task.

    Attributes:
    queryset: The queryset of all tasks.
    serializer_class: The serializer class for tasks.
    authentication_classes: The authentication classes used for this view.
    permission_classes: The permission classes required for this view.

    Methods:
    perform_update: Updates the task if the user is the creator or a staff member.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [permissions.IsAuthenticated]
    

    def perform_update(self, serializer):
        task = self.get_object()
        if task.created_by != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You do not have permission to update this task.")
        serializer.save()


class AddTagsToTaskView(generics.UpdateAPIView):
    """
    This view handles adding tags to a task.

    Attributes:
    queryset: The queryset of all tasks.
    serializer_class: The serializer class for tasks.
    permission_classes: The permission classes required for this view.
    pagination_class: The pagination class for this view.

    Methods:
    update: Adds tags to the task if the user is authenticated.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = TaskPagination 

    def update(self, request, *args, **kwargs):
        task = self.get_object()
        tags_data = request.data.get('tags', [])

        if not isinstance(tags_data, list):
            return Response({"error": "Tags must be provided as a list."}, status=status.HTTP_400_BAD_REQUEST)

        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            task.tags.add(tag)

        task.save()  

        return Response(self.get_serializer(task).data, status=status.HTTP_200_OK)
    

class TaskListView(generics.ListAPIView):
    """
    This view handles listing tasks.

    Attributes:
    queryset: The queryset of all tasks.
    serializer_class: The serializer class for tasks.
    permission_classes: The permission classes required for this view.
    authentication_classes: The authentication classes used for this view.
    filter_backends: The filter backends used for this view.
    filterset_class: The filterset class for filtering tasks.
    pagination_class: The pagination class for this view.
    ordering: The ordering of tasks.

    Methods:
    get_queryset: Returns the queryset of all tasks.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = TaskFilter
    pagination_class = TaskPagination 
    ordering = ['due_date']

    def get_queryset(self):
        return Task.objects.all()


class CommentListCreateView(generics.ListCreateAPIView):
    """
    This view handles listing and creating comments.

    Attributes:
    queryset: The queryset of all comments.
    serializer_class: The serializer class for comments.
    authentication_classes: The authentication classes used for this view.
    permission_classes: The permission classes required for this view.
    pagination_class: The pagination class for this view.

    Methods:
    perform_create: Creates a new comment with the user.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [JWTAuthentication]  # Add JWT Authentication
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = TaskPagination 
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    This view handles retrieving, updating, and deleting a single comment.

    Attributes:
    queryset: The queryset of all comments.
    serializer_class: The serializer class for comments.
    authentication_classes: The authentication classes used for this view.
    permission_classes: The permission classes required for this view.
    pagination_class: The pagination class for this view.

    Methods:
    perform_update: Updates the comment if the user is the creator or a staff member.
    perform_destroy: Deletes the comment if the user is the creator or a staff member.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = TaskPagination 

    def perform_update(self, serializer):
        comment = self.get_object()
        if comment.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You do not have permission to update this comment.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You do not have permission to delete this comment.")
        instance.delete()