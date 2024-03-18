from fastapi import APIRouter
from models.user import User
from config.db import conn
from schemas.user import usersEntity, userEntity
from bson import ObjectId

user = APIRouter()

@user.get('/')
async def find_all_users():
    return usersEntity(conn.local.user.find())

@user.get('/get_user/{id}')
async def find_user_by_id(id):
    return userEntity(conn.local.user.find_one({"_id": ObjectId(id)}))

@user.post('/create_user')
async def create_user(user: User):
    conn.local.user.insert_one(dict(user))

@user.put('/update_user/{id}')
async def update_user(id, user: User):
    conn.local.user.find_one_and_update({"_id": ObjectId(id)}, {
        "$set": dict(user)
    })
    return userEntity(conn.local.user.find_one({"_id": ObjectId(id)}))

@user.delete('/delete_user/{id}')
async def update_user(id):
    return userEntity(conn.local.user.find_one_and_delete({"_id": ObjectId(id)}))
