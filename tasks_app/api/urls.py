from django.urls import path
from .views import AssignedTaskListView, ReviewingTaskListView

urlpatterns = [
    #path(''),
    path('assigned-to-me/', AssignedTaskListView.as_view(), name='assigned-tasks'),
    path('reviewing/', ReviewingTaskListView.as_view(), name='reviewing-tasks'),
    #path('<int:pk>/'),
    #path('<int:pk>/comments/'),
    #path('<int:pk>/comments/<int:pk>')
]