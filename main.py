from database import RecipeDatabase
from scrapper import Scrapper
import asyncio


async def main():
    scrapper = Scrapper()
    result_data = await scrapper.scrap()
    db = RecipeDatabase("recipes", "recipes")

    db.populate_collection(result_data)


if __name__ == "__main__":
    asyncio.run(main())
