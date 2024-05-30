from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path(
        'relative-changes/',
        views.relative_changes_view,
        name='relative_changes'
        ),
]
