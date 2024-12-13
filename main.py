from fastapi import FastAPI, HTTPException
from databases import Database
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Float, DECIMAL, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import databases
from typing import Optional
from pydantic import BaseModel, condecimal, constr
import hashlib
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates





# Создание базового класса для моделей SQLAlchemy
Base = declarative_base()

# URL для PostgreSQL
DATABASE_URL = "postgresql://postgres:1@localhost:5432/postgres"

database = Database(DATABASE_URL)

# --- Модели Pydantic для API ---
class EditorCreate(BaseModel):
    id_editor: Optional[int] = None
    full_name: str
    position: str
    phone: str

class EditorReturn(BaseModel):
    id_editor: int
    full_name: str
    position: str
    phone: str

# Модели для Cars
class CarCreate(BaseModel):
    car_id:  Optional[str] = None
    model: str
    car_type: str
    fuel_type: str
    car_rating: condecimal(max_digits=3, decimal_places=2)
    year_to_start: int
    year_to_work: int
    riders: int
    id_editor: Optional[int]
    reserve: int

class CarReturn(BaseModel):
    car_id: str
    model: str
    car_type: str
    fuel_type: str
    car_rating: condecimal(max_digits=3, decimal_places=2)
    year_to_start: int
    year_to_work: int
    riders: int
    reserve: int

# Модели для Users
class UserCreate(BaseModel):
    user_id: Optional[str] = None
    gender: int  # 1 - мужчина, 0 - женщина
    age: int
    user_rating: condecimal(max_digits=3, decimal_places=1)

class UserReturn(BaseModel):
    user_id: str
    gender: int
    age: int
    user_rating: condecimal(max_digits=3, decimal_places=1)

# Модели для Rides
class RideCreate(BaseModel):
    user_id: Optional[str] = None
    car_id: Optional[str] = None
    ride_duration: int
    distance: condecimal(max_digits=10, decimal_places=2)
    ride_cost: condecimal(max_digits=10, decimal_places=2)

class RideReturn(BaseModel):
    user_id: str
    car_id: str
    ride_duration: int
    distance: condecimal(max_digits=10, decimal_places=2)
    ride_cost: condecimal(max_digits=10, decimal_places=2)

# --- Настройка приложения FastAPI ---
app = FastAPI()

# Подключение папки с шаблонами
templates = Jinja2Templates(directory="templates")

# Роут для отображения HTML-страницы
@app.get("/test", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Главная страница"})


@app.on_event("startup")
async def startup_database():
    try:
        await database.connect()
        print("Connected to the database successfully!")
    except Exception as e:
        print(f"Failed to connect to the database: {e}")

@app.on_event("shutdown")
async def shutdown_database():
    await database.disconnect()

# --- Роуты  для editors ---
@app.post("/editors/", response_model=EditorReturn)
async def create_editors(editors: EditorCreate):
    query = f"""INSERT INTO "Komarov_DA_A_07_22_6".editors (full_name, position, phone) 
                VALUES ('{editors.full_name}', '{editors.position}', '{editors.phone}') RETURNING id_editor"""

    try:
        id_editor = await database.execute(query=query)
        return {**editors.dict(), "id_editor": id_editor}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create editor")




























@app.put("/editors/{id_editor}", response_model=EditorReturn)
async def update_editor(id_editor: int, editors: EditorCreate):
    query = f"""
    UPDATE "Komarov_DA_A_07_22_6".editors
    SET full_name = '{editors.full_name}', position = '{editors.position}', phone = '{editors.phone}'
    WHERE id_editor = {id_editor}
    """
    try:
        await database.execute(query=query)
        return {**editors.dict(), "id_editor": id_editor}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update editor in database")

@app.delete("/editors/{id_editor}", response_model=dict)
async def delete_editor(id_editor: int):
    query = f"""
    DELETE FROM "Komarov_DA_A_07_22_6".editors
    WHERE id_editor = {id_editor}
    RETURNING id_editor
    """
    try:
        deleted_rows = await database.execute(query=query)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete editor from database")
    if deleted_rows:
        return {"message": "Editor deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Editor not found")

@app.get("/editors", response_model=List[EditorReturn])
async def get_all_editors():
    query = 'SELECT * FROM "Komarov_DA_A_07_22_6".editors'
    try:
        results = await database.fetch_all(query=query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if results:
        return [
            EditorReturn(
                id_editor=result['id_editor'],
                full_name=result["full_name"],
                position=result["position"],
                phone=result["phone"],
            )
            for result in results
        ]
    else:
        return []  # Возвращаем пустой список, если редакторов нет



























# --- Роуты для Cars ---
@app.post("/cars/", response_model=CarReturn)
async def create_car(car: CarCreate):
    query = f"""INSERT INTO "Komarov_DA_A_07_22_6".cars (car_id, model, car_type, fuel_type, car_rating, year_to_start, year_to_work, riders, id_editor)
                VALUES ('{car.car_id}', '{car.model}', '{car.car_type}', '{car.fuel_type}', {car.car_rating}, {car.year_to_start}, {car.year_to_work}, {car.riders}, {car.id_editor}, {car.reserve}) 
                RETURNING car_id"""
    try:
        car_id = await database.execute(query=query)
        return {**car.dict(), "car_id": car_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create car")

@app.put("/cars/{car_id}", response_model=CarReturn)
async def update_car(car_id: str, car: CarCreate):
    query = f"""
    UPDATE "Komarov_DA_A_07_22_6".cars
    SET model = '{car.model}', 
        car_type = '{car.car_type}', 
        fuel_type = '{car.fuel_type}', 
        car_rating = {car.car_rating}, 
        year_to_start = {car.year_to_start}, 
        year_to_work = {car.year_to_work}, 
        riders = {car.riders}, 
        id_editor = {car.id_editor},
        reserve = {car.reserve}
    WHERE car_id = '{car_id}'
    """
    try:
        await database.execute(query=query)

        return {**car.dict(), "car": car_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update car in database")

@app.delete("/cars/{car_id}", response_model=dict)
async def delete_editor(car_id: str):
    query = f"""
    DELETE FROM "Komarov_DA_A_07_22_6".cars
    WHERE car_id = '{car_id}'
    RETURNING id_editor
    """
    try:
        deleted_rows = await database.execute(query=query)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete cars from database")
    if deleted_rows:
        return {"message": "cars deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="cars not found")


@app.get("/cars", response_model=List[CarReturn])
async def get_all_cars():
    query = 'SELECT * FROM "Komarov_DA_A_07_22_6".cars'
    try:
        results = await database.fetch_all(query=query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if results:
        return [
            CarReturn(
                car_id=result["car_id"],  # Correct field name here
                model=result["model"],
                car_type=result["car_type"],
                fuel_type=result["fuel_type"],
                car_rating=result["car_rating"],
                year_to_start=result["year_to_start"],
                year_to_work=result["year_to_work"],
                riders=result["riders"],
                id_editor=result["id_editor"],
                reserve=result["reserve"]
            )
            for result in results
        ]
    else:
        return []  # Возвращаем пустой список, если машин нет





























# --- Роуты для Users ---
@app.get("/users", response_model=List[UserReturn])
async def get_all_users():
    query = 'SELECT * FROM "Komarov_DA_A_07_22_6".users'
    try:
        results = await database.fetch_all(query=query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if results:
        return [
            UserReturn(
                user_id=result["user_id"],
                gender=result["gender"],
                age=result["age"],
                user_rating=result["user_rating"],
            )
            for result in results
        ]
    else:
        return []

@app.post("/users/", response_model=UserReturn)
async def create_user(user: UserCreate):
    print(str(user))
    query = f"""INSERT INTO "Komarov_DA_A_07_22_6".users (user_id, gender, age, user_rating)
                VALUES ('{user.user_id}', {user.gender}, {user.age}, {user.user_rating}) 
                RETURNING user_id"""
    try:
        print(query)
        user_id = await database.execute(query=query)
        print(query)
        return {**user.dict(), "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create user")


@app.put("/users/{user_id}", response_model=UserReturn)
async def update_user(user_id: str, user: UserCreate):
    query = f"""
    UPDATE "Komarov_DA_A_07_22_6".users
    SET gender = {user.gender}, 
        age = {user.age}, 
        user_rating = {user.user_rating}
    WHERE user_id = '{user_id}'
    """
    try:
        await database.execute(query=query)
        return {**user.dict(), "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update user in database")


@app.delete("/users/{user_id}", response_model=dict)
async def delete_user(user_id: str):
    query = f"""
    DELETE FROM "Komarov_DA_A_07_22_6".users
    WHERE user_id = '{user_id}'
    RETURNING user_id
    """
    try:
        deleted_rows = await database.execute(query=query)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete user from database")
    if deleted_rows:
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")



























# --- Роуты для Rides ---
@app.get("/rides", response_model=List[RideReturn])
async def get_all_rides():
    query = 'SELECT * FROM "Komarov_DA_A_07_22_6".rides'
    try:
        results = await database.fetch_all(query=query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if results:
        return [
            RideReturn(
                user_id=result["user_id"],
                car_id=result["car_id"],
                ride_duration=result["ride_duration"],
                distance=result["distance"],
                ride_cost=result["ride_cost"],
            )
            for result in results
        ]
    else:
        return []

@app.post("/rides/", response_model=RideReturn)
async def create_ride(ride: RideCreate):
    query = f"""INSERT INTO "Komarov_DA_A_07_22_6".rides (user_id, car_id, ride_duration, distance, ride_cost)
                VALUES ('{ride.user_id}', '{ride.car_id}', {ride.ride_duration}, {ride.distance}, {ride.ride_cost}) 
                RETURNING ride_id"""
    try:
        ride_id = await database.execute(query=query)
        return {**ride.dict(), "ride_id": ride_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create ride")


@app.put("/rides/{ride_id}", response_model=RideReturn)
async def update_ride(ride_id: str, ride: RideCreate):
    query = f"""
    UPDATE "Komarov_DA_A_07_22_6".rides
    SET user_id = '{ride.user_id}', 
        car_id = '{ride.car_id}', 
        ride_duration = {ride.ride_duration}, 
        distance = {ride.distance}, 
        ride_cost = {ride.ride_cost}
    WHERE ride_id = '{ride_id}'
    """
    try:
        await database.execute(query=query)
        return {**ride.dict(), "ride_id": ride_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update ride in database")


@app.delete("/rides/{ride_id}", response_model=dict)
async def delete_ride(ride_id: str):
    query = f"""
    DELETE FROM "Komarov_DA_A_07_22_6".rides
    WHERE ride_id = '{ride_id}'
    RETURNING ride_id
    """
    try:
        deleted_rows = await database.execute(query=query)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete ride from database")
    if deleted_rows:
        return {"message": "Ride deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Ride not found")

