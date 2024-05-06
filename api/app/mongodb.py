from pymongo import MongoClient


class MongoDBClient:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["chargify"]

        self.commutes = self.db["commutes"]
        self.car_models = self.db["car_models"]
        self.users = self.db["users"]

    def insert_user(self, user):
        collection = self.db["users"]

        result = collection.insert_one(user)

        return result.inserted_id

    def find_user_by_id(self, user_id: int):
        collection = self.db["users"]

        return collection.find_one({"_id": user_id})

    def find_user_by_name(self, name: str):
        collection = self.db["users"]

        return collection.find_one({"name": name})

    def insert_car_model(self, car_model):
        collection = self.db["car_models"]

        result = collection.insert_one(car_model)

        return result.inserted_id

    def find_car_model_by_id(self, car_model_id: int):
        collection = self.db["car_models"]

        return collection.find_one({"id": car_model_id})

    def find_car_model_by_name(self, name: str):
        collection = self.db["car_models"]

        return collection.find_one({"name": name})

    def insert_commute(self, commute):
        collection = self.db["commutes"]

        result = collection.insert_one(commute)

        return result.inserted_id

    def find_commutes_by_user_id(self, user_id: str):
        collection = self.db["commutes"]

        return collection.find({"userId": user_id})
