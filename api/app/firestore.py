import pathlib
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# ideally this should be in an environment and not publicly stored
path = pathlib.Path(__file__).parent / "serviceAccount.json"
cred = credentials.Certificate(path)

app = firebase_admin.initialize_app(cred)

db = firestore.client()
