from django.urls import path

from . import views

# register namespace
app_name = 'app'

# register dispatch
urlpatterns = (
    path('', views.index, name='index'),
)
