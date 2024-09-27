import json

from bs4 import BeautifulSoup
import requests


def get_amount(s):
    amount = s.split()[0]
    if amount.isnumeric():
        return int(amount)
    else:
        return 1


class Scrapper:
    def __init__(self):
        self.main_containers = None
        self.soup = None
        self.base_url = "https://kulinaria.ge"
        self.recipes = f"{self.base_url}/receptebi"
        self.categories = f"{self.recipes}/cat"
        self.target_category = f"{self.categories}/pasta-da-burRuleuli"

    def scrap(self):
        main_page = requests.get(self.target_category)
        self.soup = BeautifulSoup(main_page.text, "html.parser")
        self.main_containers = []
        first_container = self.soup.find(attrs={"class": "section"}).find(attrs={"class": "box-container"})

        self.main_containers.append(first_container)

        result = []

        self.scrap_pages(result)

        return result

    def scrap_pages(self, result):
        while len(self.main_containers) > 0:
            container = self.main_containers.pop(0)
            items = container.find_all("div", recursive=False)

            for item in items:
                if "endless_container" in item["class"]:
                    next_page_uri = item.find("a")["href"]
                    next_page_url = f"{self.base_url}{next_page_uri}"
                    next_page = requests.get(next_page_url)
                    soup = BeautifulSoup(next_page.text, "html.parser")
                    container = soup.find(attrs={"class": "section"}).find(attrs={"class": "box-container"})
                    self.main_containers.append(container)

                else:
                    self.scrap_item(item, result)

    def scrap_item(self, item, result):
        recipe = {}
        img_box = item.find("div", attrs={"class": "box__img"})
        box_space = item.find("div", attrs={"class": "box-space"})

        url_and_title = box_space.find("a")

        # 1. title of recipe
        title = url_and_title.contents[0].strip()
        recipe["title"] = title

        # 2. recipe url
        url = url_and_title["href"]
        recipe["url"] = f"{self.base_url}{url}"

        # 3. main image url
        image_uri = img_box.find("img")["src"]
        image_url = f"{self.base_url}{image_uri}"
        recipe["image_url"] = image_url

        # 4. description
        short_description = box_space.find("div", attrs={"class": "box__desc"}).contents[0].strip()
        recipe["short_description"] = short_description

        # 5. author name
        author = box_space.find("div", attrs={"class": "name"}).find("a").contents[0].strip()
        recipe["author"] = author

        # now scrapping recipe page itself
        recipe_page = requests.get(recipe["url"])
        soup = BeautifulSoup(recipe_page.text, "html.parser")

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

        category = {"name": category_name, "url": category_url}
        subcategory = {"name": subcategory_name, "url": subcategory_url}

        recipe["category"] = category
        recipe["subcategory"] = subcategory

        result.append(recipe)
