from fastapi import APIRouter
from schemas import CommuteEntity
from mongodb import MongoDBClient

router = APIRouter(prefix="/commutes", tags=["commutes"])
db = MongoDBClient()


@router.get("/", response_model=list[CommuteEntity])
async def get_commutes(user_id: str) -> list[CommuteEntity]:
    """Get all the commutes filtered by a specific user."""

    # Get all the commutes
    result = db.find_commutes_by_user_id(user_id=user_id)

    # Return the commutes
    return [CommuteEntity(**commute) for commute in result]


@router.post("/")
async def add_commute(commute: CommuteEntity):
    """Add a new commute to the database."""
    try:
        print(commute.to_dict())
        commute_id = db.insert_commute(commute.to_dict())

        return {"id": str(commute_id), "message": "Commute added successfully!"}
    except Exception as e:  # pylint: disable=W0718
        print(e)
        return e
