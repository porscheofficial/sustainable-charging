from fastapi import APIRouter

from mongodb import MongoDBClient
from schemas import CarModel

db = MongoDBClient()
router = APIRouter(prefix="/car_model", tags=[" car model"])


@router.post("/")
async def add_car_model(car_model: CarModel):
    """
    Add a new car model to the database.
    """
    try:
        car_model_id = db.insert_car_model(car_model.to_dict())

        return {"id": str(car_model_id), "message": "Car model added successfully!"}
    except Exception as e:  # pylint: disable=W0718
        return e
