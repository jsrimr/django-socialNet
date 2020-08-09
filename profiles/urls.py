from django.urls import path

from .views import my_profile_view, invites_received_view

app_name = 'profiles'

urlpatterns = [
    path('myprofile/', my_profile_view, name='my-profile-view'),
    path('my-invites', invites_received_view, name='my-invites-view')
]
