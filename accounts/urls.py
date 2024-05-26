from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),  # URL de login
    path('logout/', views.logout_view, name='logout'),  # URL de logout
]
