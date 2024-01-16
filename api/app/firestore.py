import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

# ideally this should be in an environment and not publicly stored
path = os.path.abspath(os.path.dirname(__file__)) + "/serviceAccount.json"
cred = credentials.Certificate(path)

app = firebase_admin.initialize_app(cred)

db = firestore.client()
