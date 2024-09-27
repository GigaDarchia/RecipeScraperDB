from database import RecipeDatabase
from scrapper import Scrapper
import asyncio

async def main():
    scrapper = Scrapper()
    result_data = await scrapper.scrap()
    db = RecipeDatabase("recipes", "recipes")

    db.populate_collection(result_data)

    db.get_average_ingredients()
    db.get_average_steps()
    db.get_recipe_with_most_portions()
    db.fetch_author_with_most_recipes()

    db.close()


if __name__ == "__main__":
    asyncio.run(main())

