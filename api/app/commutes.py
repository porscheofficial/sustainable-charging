from fastapi import APIRouter
from app.firestore import db
from app.schemas import CommuteEntity

router = APIRouter(
    prefix='/commutes',
    tags=['commutes']
)

@router.get("/", response_model=list[CommuteEntity])
async def get_commutes(user_id: str) -> list[CommuteEntity]:
    """
    Get all the commutes filtered by a specific user.
    """
    
    # Get all the commutes
    commutes = db.collection('commutes').where('user_id', '==', user_id).stream()

    # Return the commutes
    return [CommuteEntity(**commute.to_dict()) for commute in commutes]

@router.post("/")
async def add_commute(commute: CommuteEntity):
    """
    Add a new commute to the database.
    """

    # Create a new document reference with an auto-generated ID
    doc_ref = db.collection('commutes').document()

    # Save the commute data
    doc_ref.set(commute.model_dump())

    # TODO: Call the scheduler to schedule the commute and store it in the database (@william)
    # We can either store it in the same document or create a new collection for scheduled commutes and reference the commute ID

    # Return the ID of the newly created document
    return {"id": doc_ref.id, "message": "Commute added successfully!"}

