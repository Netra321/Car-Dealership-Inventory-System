from fastapi import FastAPI
from sqlmodel import SQLModel, Field, create_engine, Session, select
from fastapi import Query

app = FastAPI()

DATABASE_URL = "sqlite:///car_dealership.db"
engine = create_engine(DATABASE_URL)


class Vehicle(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    make: str
    model: str
    category: str
    price: float
    quantity: int


SQLModel.metadata.create_all(engine)

@app.get("/")
def home():
    return {"message": "Car Dealership Inventory API is running!"}


@app.post("/vehicles")
def add_vehicle(vehicle: Vehicle):
    with Session(engine) as session:
        session.add(vehicle)
        session.commit()
        session.refresh(vehicle)
        return vehicle


@app.get("/vehicles/search")
def search_vehicle(make: str = Query(None)):
    with Session(engine) as session:
        statement = select(Vehicle)

        if make:
            statement = statement.where(Vehicle.make == make)

        vehicles = session.exec(statement).all()
        return vehicles


@app.get("/vehicles")
def get_vehicles():
    with Session(engine) as session:
        vehicles = session.exec(select(Vehicle)).all()
        return vehicles

@app.put("/vehicles/{vehicle_id}")
def update_vehicle(vehicle_id: int, updated_vehicle: Vehicle):
    with Session(engine) as session:
        vehicle = session.get(Vehicle, vehicle_id)

        if not vehicle:
            return {"message": "Vehicle not found"}

        vehicle.make = updated_vehicle.make
        vehicle.model = updated_vehicle.model
        vehicle.category = updated_vehicle.category
        vehicle.price = updated_vehicle.price
        vehicle.quantity = updated_vehicle.quantity

        session.add(vehicle)
        session.commit()
        session.refresh(vehicle)

        return vehicle


@app.post("/vehicles/{vehicle_id}/purchase")
def purchase_vehicle(vehicle_id: int):
    with Session(engine) as session:
        vehicle = session.get(Vehicle, vehicle_id)

        if vehicle is None:
            return {"message": "Vehicle not found"}

        if vehicle.quantity <= 0:
            return {"message": "Vehicle out of stock"}

        vehicle.quantity -= 1

        session.commit()
        session.refresh(vehicle)

        return vehicle
    

@app.post("/vehicles/{vehicle_id}/restock")
def restock_vehicle(vehicle_id: int):
    with Session(engine) as session:
        vehicle = session.get(Vehicle, vehicle_id)

        if vehicle is None:
            return {"message": "Vehicle not found"}

        vehicle.quantity += 1

        session.commit()
        session.refresh(vehicle)

        return vehicle