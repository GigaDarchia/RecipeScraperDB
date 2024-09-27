from pymongo import MongoClient
from pymongo.errors import PyMongoError


class RecipeDatabase:

    def __init__(self, db_name, collection_name):
        self.client = MongoClient("localhost", 27017)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def populate_collection(self, recipe_data: list):
        try:
            self.collection.insert_many(recipe_data)
        except PyMongoError as e:
            print(f"Error while inserting data: {e}")

    def close(self):
        self.client.close()

    def get_average_ingredients(self):
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "avg_ingredients": {"$avg": {"$size": "$ingredients"}}
                }
            }
        ]
        try:
            result = list(self.collection.aggregate(pipeline))
            if result:
                print(f"Average ingredients needed: {result[0]['avg_ingredients']:.0f}")
            else:
                print("No data found.")
        except PyMongoError as e:
            print(f"Error while aggregating data: {e}")
        print("-" * 100)

    def get_average_steps(self):
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "avg_steps": {"$avg": {"$size": "$etapebi"}}
                }
            }
        ]
        try:
            result = list(self.collection.aggregate(pipeline))
            if result:
                print(f"Average steps needed: {result[0]['avg_steps']:.0f}")
            else:
                print("No data found.")
        except PyMongoError as e:
            print(f"Error while aggregating data: {e}")
        print("-" * 100)

    def get_recipe_with_most_portions(self):
        pipeline = [
            {
                "$group": {
                    "_id": "$title",
                    "portions": {"$max": "$ulufebi"}
                }
            }
        ]
        try:
            result = list(self.collection.aggregate(pipeline))
            if result:
                print(f"Recipe with most portions: {result[0]['_id']} - {result[0]['portions']} portions")
            else:
                print("No data found.")
        except PyMongoError as e:
            print(f"Error while aggregating data: {e}")
        print("-" * 100)

    def fetch_author_with_most_recipes(self):
        pipeline = [
            {
                "$group": {
                    "_id": "$author",
                    "recipeCount": {"$sum": 1}
                }
            },
            {
                "$sort": {
                    "recipeCount": -1
                }
            },
            {
                "$limit": 1
            }
        ]
        try:
            result = list(self.collection.aggregate(pipeline))
            if result:
                print("Author with most recipes: ")
                print(f"Author: {result[0]['_id']} | Number of recipes: {result[0]['recipeCount']}")
            else:
                print("No data found.")
        except PyMongoError as e:
            print(f"Error while aggregating data: {e}")
        print("-" * 100)
