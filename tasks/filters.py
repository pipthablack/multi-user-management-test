import django_filters
from .models import Task, Tag

class TaskFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(field_name='status', lookup_expr='icontains')

    class Meta:
        model = Task
        fields = ['status', 'due_date', 'tags']
