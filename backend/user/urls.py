from django.urls import path, re_path
from rest_framework.authtoken.views import obtain_auth_token
from .views import getUserData

urlpatterns = [ 
    path('getuserdata/', getUserData, name='userData'),   
    path('token/', obtain_auth_token, name='api_token_auth'),   
]