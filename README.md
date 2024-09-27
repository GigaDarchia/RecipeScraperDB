# Recipe Scrapper and Analyzer

This project is designed to scrape recipe data from a website and save it into a MongoDB database. It then allows you to perform various analyses on the stored recipe data.

## Features
- Scrape recipe information from a specified website.
- Store recipe data in a MongoDB database.
- Perform aggregation analysis on the stored data, including:
  - Finding the average number of ingredients.
  - Finding the average number of steps.
  - Finding the recipe with the most portions.
  - Finding the author with the most recipes.

## Prerequisites
- Python 3.12.5
- MongoDB running on localhost at the default port (27017)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/GigaDarchia/RecipeScraperDB.git
   cd RecipeScraperDB
   ```

2. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
   The `requirements.txt` file should contain:
   ```plaintext
   beautifulsoup4
   aiohttp
   pymongo
   ```

3. Ensure MongoDB is running on your machine:
   ```bash
   mongod
   ```

## Usage
1. Run the script using:
   ```bash
   python main.py
   ```

## Code Structure
- `database.py`: Contains the `RecipeDatabase` class which handles the connection to MongoDB and methods to perform various data analysis.
- `scrapper.py`: Contains the `Scrapper` class which uses `aiohttp` and `BeautifulSoup` to scrape recipe data asynchronously.
- `main.py`: Entry point of the project. It initializes the scrapper, scrapes the data, populates the database, and performs data analysis.

