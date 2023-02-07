from fastapi import FastAPI, HTTPException, Body
from datetime import date
from pymongo import MongoClient
from pydantic import BaseModel

DATABASE_NAME = "exceed07"
COLLECTION_NAME = "reservation_phukit"
MONGO_DB_URL = "mongodb://exceed07:8td6VF6w@mongo.exceed19.online:8443/?authMechanism=DEFAULT"
MONGO_DB_PORT = 8443


class Reservation(BaseModel):
    name : str
    start_date: date
    end_date: date
    room_id: int


client = MongoClient(f"{MONGO_DB_URL}:{MONGO_DB_PORT}")

db = client[DATABASE_NAME]

collection = db[COLLECTION_NAME]

app = FastAPI()


def room_avaliable(room_id: int, start_date: str, end_date: str):
    query={"room_id": room_id,
           "$or": 
                [{"$and": [{"start_date": {"$lte": start_date}}, {"end_date": {"$gte": start_date}}]},
                 {"$and": [{"start_date": {"$lte": end_date}}, {"end_date": {"$gte": end_date}}]},
                 {"$and": [{"start_date": {"$gte": start_date}}, {"end_date": {"$lte": end_date}}]}]
            }
    
    result = collection.find(query, {"_id": 0})
    list_cursor = list(result)

    return not len(list_cursor) > 0


@app.get("/reservation/by-name/{name}")
def get_reservation_by_name(name:str):
    hotel = []
    for i in collection.find({"name": name}, {"_id":False}):
        hotel.append(i)
    return {"result": hotel}


@app.get("/reservation/by-room/{room_id}")
def get_reservation_by_room(room_id: int):
    hotel = []
    for i in collection.find({"room_id": room_id}, {"_id":False}):
        hotel.append(i)
    return {"result": hotel}

@app.post("/reservation")
def reserve(reservation : Reservation):
    if not room_avaliable(reservation.room_id, str(reservation.start_date), str(reservation.end_date)):
        raise HTTPException(status_code=400)
    if reservation.start_date > reservation.end_date:
        raise HTTPException(status_code=400)
    if reservation.room_id not in range(1,11):
        raise HTTPException(status_code=400)
    collection.insert_one({
        "name": reservation.name, 
        "start_date": str(reservation.start_date), 
        "end_date": str(reservation.end_date), 
        "room_id": reservation.room_id
        })

@app.put("/reservation/update")
def update_reservation(reservation: Reservation, new_start_date: date = Body(), new_end_date: date = Body()):
    if not room_avaliable(reservation.room_id, str(reservation.start_date), str(reservation.end_date)):
        raise HTTPException(status_code=400)
    if reservation.start_date > reservation.end_date:
        raise HTTPException(status_code=400)
    if reservation.room_id not in range(1,11):
        raise HTTPException(status_code=400)
    new_start_date = new_start_date.strftime("%Y-%m-%d")
    new_end_date = new_end_date.strftime("%Y-%m-%d")
    if new_start_date < new_end_date:
        collection.update_one({
            "name": reservation.name, 
            "room_id": reservation.room_id}, 
            {"$set": {
                "start_date": str(new_start_date), 
                "end_date": str(new_end_date)
                }
            })

@app.delete("/reservation/delete")
def cancel_reservation(reservation: Reservation):
    collection.delete_one({
        "name": reservation.name, 
        "start_date": str(reservation.start_date), 
        "end_date": str(reservation.end_date), 
        "room_id": reservation.room_id
        })
