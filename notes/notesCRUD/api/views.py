from django.shortcuts import render
from pymongo import MongoClient, ReturnDocument
from decouple import config
from rest_framework.views import APIView
from datetime import datetime
import math
import random
from django.contrib.auth.hashers import make_password, check_password
from bson.objectid import ObjectId
from core.response import *
from core.authentication import *


client = MongoClient(config('MONGO_CONNECTION_STRING'))

db = client.notes_record

def valueEntity(item) -> dict:
    if item is not None:
        for key, value in item.items():
            if ObjectId.is_valid(value):
                item[key] = str(item[key])
        return item
    return None


def valuesEntity(entity) -> list:
    return [valueEntity(item) for item in entity]


#--------------- Create User API -------------#

class CreateUser(APIView):

    def post(self, request):
        data = request.data
        print("data", data)
        if data["first_name"] != "" and data["first_name"] != None and data["last_name"] != "" and data["last_name"] != None and data["email"] != "":
            existingUser = db.users.find_one({"email" : data["email"]})
            if not existingUser:
                obj = {
                    "first_name" : data["first_name"],
                    "last_name" : data["last_name"],
                    "email": data["email"],
                    "role": "User",
                    "created_at" : datetime.datetime.now(),
                    "updated_at": ""
                }
                db.users.insert_one(obj)
                return onSuccess("user created successfully.",1)
            else:
                return badRequest("User is already exist.")
        else:
            return badRequest("All the fields are required.")


#------------ Create Admin -------------#

class CreateAdmin(APIView):

    def post(self, request):
        data = request.data
        if data["first_name"] != "" and data["last_name"] != "" and data["email"] != "":
            existingUser = db.users.find_one({"email" : data["email"]})
            if not existingUser:
                obj = {
                    "first_name" : data["first_name"],
                    "last_name" : data["last_name"],
                    "email": data["email"],
                    "role": "Admin",
                    "created_at" : datetime.datetime.now(),
                    "updated_at": ""
                }
                db.users.insert_one(obj)
                return onSuccess("Admin created successfully.",1)
            else:
                return badRequest("User is already exist.")
        else:
            return badRequest("All the fields are required.")


#------------ Login Admin ------------#

class LoginAdmin(APIView):
    
    def post(self, request):
        data = request.data
        if data["email"] != "":
            get_admin = db.users.find_one({"email": data["email"], "role": "Admin"})
            if get_admin is not None:
                token = create_access_token(get_admin["_id"])
                return onSuccess("Admin Login successful.", token)
            else:
                return badRequest("user not found.")
        else:
            return badRequest("email is must to login")
        
#--------------- Login User -----------#

class LoginUser(APIView):
    
    def post(self, request):
        data = request.data
        if data["email"] != "":
            get_user = db.users.find_one({"email": data["email"], "role": "User"})
            if get_user is not None:
                token = create_access_token(get_user["_id"])
                return onSuccess("User Login successful.", token)
            else:
                return badRequest("user not found.")
        else:
            return badRequest("email is must to login")


#-------------- Get All notes -------------#

class AllNotes(APIView):

    def get(self, request):
        token =  authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            all_notes = valuesEntity(db.notes.find().sort("createdAt", -1))
            return onSuccess("All notes", all_notes)
        else:
            return unauthorisedRequest()

#----------------- Notes CRUD ---------------#

class NotesCrud(APIView):
    
    def get(self,request):
        token =  authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            data = request.data
            if ObjectId().is_valid(data["note_id"]):
                get_note = valueEntity(db.notes.find_one({"_id": ObjectId(data["note_id"])}))
                if get_note:
                    return onSuccess("Note by given id", get_note)
                else:
                    return badRequest("Note not found.")
            else:
                return badRequest("Note id is not valid.")
        else:
            return unauthorisedRequest()

    def post(self, request):
        token =  authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            data = request.data
            if data["title"] != "" and data["content"] != "":
                obj = {
                    "title": data["title"],
                    "content": data["content"],
                    "created_by": ObjectId(token["_id"]),
                    "updated_by": "",
                    "createdAt": datetime.datetime.now(),
                    "updatedAt": ""
                }
                db.notes.insert_one(obj)
                return onSuccess("Note created successfully.", 1)
            else:
                return badRequest("All the fields are required.")
        else:
            return unauthorisedRequest()

        
    def put(self, request):
        token =  authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            data = request.data
            if ObjectId().is_valid(data["note_id"]):
                if data["note_id"] != "" and data["title"] != "":
                    get_note = db.notes.find_one({"_id": ObjectId(data["note_id"])})
                    if get_note:
                        new_obj = { "$set": { 'title': data["title"],
                                                'content': data["content"],
                                                "updated_by": ObjectId(token["_id"]),
                                                'updatedAt': datetime.datetime.now()
                                            }
                        }
                        updated_obj = db.notes.find_one_and_update({"_id" : ObjectId(get_note["_id"])}, new_obj)
                        get_updated_obj = db.notes.find_one({"_id": updated_obj["_id"]})
                        return onSuccess("Note updated successfully.", valueEntity(get_updated_obj))
                    else:
                        return badRequest("note not found.")
                else:
                    return badRequest("title can not be blank.")
            else:
                return badRequest("Note id is not valid.")
        else:
            return unauthorisedRequest() 
    
    def delete(self, request):
        token =  authenticate(request)
        if token and ObjectId().is_valid(token["_id"]):
            data = request.data
            if ObjectId().is_valid(data["note_id"]):
                get_note = db.notes.find_one({"_id": ObjectId(data["note_id"])})
                if get_note:
                    db.notes.delete_one(get_note)
                    return onSuccess("Note deleted successfully.", 1)
                else:
                    return badRequest("note not found.")
            else:
                return badRequest("Note id is not valid.") 
        else:
            return unauthorisedRequest()

         



