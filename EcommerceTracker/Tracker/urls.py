from django.urls import path , include
from Tracker import views

urlpatterns = [
    path('' , views.home , name='Home'),
    path('track/' , views.Track , name='Track'),
    path('delete/<int:Id>/' , views.delete , name='DeleteId')

]
