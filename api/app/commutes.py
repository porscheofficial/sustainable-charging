from datetime import datetime
from fastapi import APIRouter
from firestore import db
from schemas import CommuteEntity
import datetime

router = APIRouter(
    prefix='/commutes',
    tags=['commutes']
)

@router.get("/", response_model=list[CommuteEntity])
async def get_commutes() -> list[CommuteEntity]:
    """
    Get all the commutes (not user specific yet)
    """
    
    # Get all the commutes
    commutes = db.collection('commutes').stream()

    # Return the commutes
    return [commute.to_dict() for commute in commutes]

@router.post("/")
async def add_commute(commute: CommuteEntity):
    """
    Add a new commute (not user specific yet)
    """

    # Create a new document reference with an auto-generated ID
    doc_ref = db.collection('commutes').document()

    # Save the commute data
    doc_ref.set(commute.model_dump())

    # TODO: Call the scheduler to schedule the commute and store it in the database (@william)
    # We can either store it in the same document or create a new collection for scheduled commutes and reference the commute ID

    # Return the ID of the newly created document
    return {"id": doc_ref.id, "message": "Commute added successfully!"}

