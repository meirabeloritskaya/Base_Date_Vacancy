import os
from dotenv import load_dotenv
from src.api_service import HeadHunterAPI
import logging

logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(BASE_DIR, "logs", "vacancy_manager.log")
file_handler = logging.FileHandler(path, encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


load_dotenv()
MY_BASE_URL = os.getenv("BASE_URL")

hh_api = HeadHunterAPI(MY_BASE_URL)

# Список работодателей для получения данных
employers = ["ABCP", "prosto", "Pixel", "Coddy", "JETCODE", "Code-Class", "Atem", "F5it", "HeadHunter", "iStaff-IT"]

for employer in employers:
    employer_id = hh_api.get_employer_id(employer)
    if employer_id:
        vacancies = hh_api.get_vacancies_by_employer(employer_id)
        print(f"Vacancies for {employer}:")
        for vacancy in vacancies:
            print(f"- {vacancy['name']}: {vacancy['alternate_url']}")
    else:
        print(f"No vacancies found for {employer}")
