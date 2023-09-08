from django.urls import path
from .views import *

urlpatterns = [
    path('create-user', CreateUser.as_view(), name="CreateUser"),

    path('create-admin', CreateAdmin.as_view(), name="CreateAdmin"),
    
    path('all-notes', AllNotes.as_view(), name="AllNotes"),

    #----------- Create Notes----------#
    path('create-note', NotesCrud.as_view(), name="NotesCrud"),
    path('get-note', NotesCrud.as_view(), name="NotesCrud"),
    path('update-note', NotesCrud.as_view(), name="NotesCrud"),
    path('delete-note', NotesCrud.as_view(), name="NotesCrud"),

    path('login-admin', LoginAdmin.as_view(), name="LoginAdmin"),
    path('login-user', LoginUser.as_view(), name="LoginUser"),




]