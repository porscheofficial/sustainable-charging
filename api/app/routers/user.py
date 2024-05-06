from fastapi import APIRouter

from mongodb import MongoDBClient
from schemas import User

db = MongoDBClient()
router = APIRouter(prefix="/user", tags=["user"])


@router.post("/")
async def add_user(user: User):
    """
    Add a new user to the database.
    """
    try:
        user_id = db.insert_user(user.to_dict())

        return {"id": str(user_id), "message": "User added successfully!"}
    except Exception as e:  # pylint: disable=W0718
        return e
