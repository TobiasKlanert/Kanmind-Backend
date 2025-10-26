from django.urls import path
from .views import CreateTaskView, AssignedTaskListView, ReviewingTaskListView

urlpatterns = [
    path('', CreateTaskView.as_view(), name='create-task'),
    path('assigned-to-me/', AssignedTaskListView.as_view(), name='assigned-tasks'),
    path('reviewing/', ReviewingTaskListView.as_view(), name='reviewing-tasks'),
    #path('<int:pk>/'),
    #path('<int:pk>/comments/'),
    #path('<int:pk>/comments/<int:pk>')
]