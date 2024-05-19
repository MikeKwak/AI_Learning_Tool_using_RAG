from django.urls import path
from .views import process_documents, ask_question, register, confirm_registration_view, login, logout

urlpatterns = [
    path('register/', register, name='register'),
    path('confirm/', confirm_registration_view, name='confirm'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('process_documents/', process_documents, name='process_documents'),
    path('ask_question/', ask_question, name='ask_question'),
]