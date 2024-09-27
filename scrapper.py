from bs4 import BeautifulSoup
import asyncio
import aiohttp
import threading


def get_amount(s):
    amount = s.split()[0]
    if amount.isnumeric():
        return int(amount)
    else:
        return 1


async def fetch(url, session):
    async with session.get(url) as response:
        return await response.text()


class Scrapper:
    def __init__(self):
        self.main_containers = None
        self.soup = None
        self.base_url = "https://kulinaria.ge"
        self.recipes = f"{self.base_url}/receptebi"
        self.categories = f"{self.recipes}/cat"
        self.target_category = f"{self.categories}/pasta-da-burRuleuli"
        self.result_lock = threading.Lock()

    async def scrap(self):
        async with aiohttp.ClientSession() as session:
            main_page = await fetch(self.target_category, session)
            self.soup = BeautifulSoup(main_page, "html.parser")
            self.main_containers = []
            first_container = self.soup.find(attrs={"class": "section"}).find(attrs={"class": "box-container"})
            self.main_containers.append(first_container)

            result = []
            await self.scrap_pages(result, session)
            return result

    async def scrap_pages(self, result, session):
        while len(self.main_containers) > 0:
            container = self.main_containers.pop(0)
            items = container.find_all("div", recursive=False)

            tasks = []
            for item in items:
                if "endless_container" in item["class"]:
                    next_page_uri = item.find("a")["href"]
                    next_page_url = f"{self.base_url}{next_page_uri}"
                    tasks.append(self.handle_next_page(next_page_url, session))
                else:
                    tasks.append(self.scrap_item(item, result, session))

            await asyncio.gather(*tasks)

    async def handle_next_page(self, next_page_url, session):
        next_page = await fetch(next_page_url, session)
        soup = BeautifulSoup(next_page, "html.parser")
        container = soup.find(attrs={"class": "section"}).find(attrs={"class": "box-container"})
        self.main_containers.append(container)

    async def scrap_item(self, item, result, session):
        recipe = {}
        img_box = item.find("div", attrs={"class": "box__img"})
        box_space = item.find("div", attrs={"class": "box-space"})

        # 1. title of recipe
        url_and_title = box_space.find("a")
        title = url_and_title.contents[0].strip()
        recipe["title"] = title

        # 2. recipe url
        url = url_and_title["href"]
        recipe["url"] = f"{self.base_url}{url}"

        # 3. main image url
        image_uri = img_box.find("img")["src"]
        recipe["image_url"] = f"{self.base_url}{image_uri}"

        # 4. description
        short_description = box_space.find("div", attrs={"class": "box__desc"}).contents[0].strip()
        recipe["short_description"] = short_description

        # 5. author name
        author = box_space.find("div", attrs={"class": "name"}).find("a").contents[0].strip()
        recipe["author"] = author

        # Now scrap the recipe page itself
        recipe_page = await fetch(recipe["url"], session)
        soup = BeautifulSoup(recipe_page, "html.parser")

        # 6. number of portions
        portion_container = soup.find_all("div", attrs={"class": "lineDesc__item"})[1]
        unformatted_portions = portion_container.get_text()
        formatted_portions = ' '.join(unformatted_portions.split())
        portion_amount = get_amount(formatted_portions)
        recipe["portions"] = portion_amount

        # 7. ingredients
        ingredients = []
        ingredients_list = soup.find("div", attrs={"class": "list"}).find_all(recursive=False)
        for ingredient in ingredients_list:
            unformatted_ingredient = ingredient.get_text()
            formatted_ingredient = ' '.join(unformatted_ingredient.split())
            ingredients.append(formatted_ingredient)
        recipe["ingredients"] = ingredients

        # 8. steps
        steps = {}
        steps_list = soup.find("div", attrs={"class": "lineList"}).find_all(recursive=False)
        for step in steps_list:
            step_number = step.find("div", attrs={"class": "count"}).get_text()
            step_description = step.find("p").get_text()
            steps[step_number] = step_description
        recipe["steps"] = steps

        # 9-10. category and subcategory
        categories = (soup.find("div", attrs={"class": "pagination-container"})
                      .find_all(attrs={"class": "pagination__item"}))
        category_name = categories[2].get_text()
        category_uri = categories[2]["href"]
        category_url = f"{self.base_url}{category_uri}"

        subcategory_name = categories[3].get_text()
        subcategory_uri = categories[3]["href"]
        subcategory_url = f"{self.base_url}{subcategory_uri}"

        recipe["category"] = {"name": category_name, "url": category_url}
        recipe["subcategory"] = {"name": subcategory_name, "url": subcategory_url}

        self.result_lock.acquire()
        result.append(recipe)
        self.result_lock.release()


