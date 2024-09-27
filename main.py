from database import RecipeDatabase
from scrapper import Scrapper

db = RecipeDatabase("recipes", "recipes")
scrapper = Scrapper()
result_data = scrapper.scrap()
db.populate_collection(result_data)
