from abc import ABC, abstractmethod
import logging
import requests
import os
from dotenv import load_dotenv


logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(BASE_DIR, "logs", "api_service.log")
file_handler = logging.FileHandler(path, encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


class WebsiteAPI(ABC):
    """абстрактный класс для парсинга вакансий"""

    @abstractmethod
    def get_employer_id(self, employer_name: str):
        """Получение ID работодателя по имени"""
        pass

    @abstractmethod
    def get_vacancies_by_employer(self, employer_id: int):
        """Получение вакансий по ID работодателя"""
        pass


class HeadHunterAPI(WebsiteAPI):
    """Класс для получения списка вакансий с сайта HeadHunter."""

    def __init__(self, base_url: str):
        """Инициализирует HeadHunterAPI с базовым URL"""
        logger.info("получение информации о вакансиях")
        self.base_url = base_url
        self.headers = {"User-Agent": "HH-User-Agent"}
        self.params = {"per_page": 10, "page": 0}
        self.vacancies = []

    def get_employer_id(self, employer_name: str):
        """Получение ID работодателя по имени"""
        search_url = f'{self.base_url}/employers'
        params = {"text": employer_name}
        try:
            response = requests.get(url=search_url, headers=self.headers, params=params)
            response.raise_for_status()
            logger.info(f"Запрос успешно выполнен для поиска работодателя: {employer_name}")

            data = response.json()
            items = data.get("items", [])
            if items:
                return items[0]['id']
            else:
                logger.warning(f"Работодатель '{employer_name}' не найден")
                return None

        except requests.RequestException as e:
            logger.error(f"Ошибка запроса к API при поиске работодателя: {e}")
            raise

    def get_vacancies_by_employer(self, employer_id: int):
        """Получение вакансий по ID работодателя"""
        if not employer_id:
            logger.error("ID работодателя не задан")
            raise ValueError("ID работодателя не задан")
        vacancies_url = f'{self.base_url}/vacancies'
        params = {"employer_id": employer_id}
        try:
            response = requests.get(url=vacancies_url, headers=self.headers, params=params)
            response.raise_for_status()
            logger.info(f"Запрос успешно выполнен для вакансий работодателя с ID {employer_id}")

            data = response.json()
            return data.get("items", [])

        except requests.RequestException as e:
            logger.error(f"Ошибка запроса к API при получении вакансий: {e}")
            raise


if __name__ == "__main__":
    load_dotenv()
    MY_BASE_URL = os.getenv("BASE_URL")
    hh_api = HeadHunterAPI(MY_BASE_URL)

    # Список работодателей для получения данных
    employers = ["Company 1", "Company 2", "Company 3", "Company 4", "Company 5",
                 "Company 6", "Company 7", "Company 8", "Company 9", "Company 10"]

    for employer in employers:
        employer_id = hh_api.get_employer_id(employer)
        if employer_id:
            vacancies = hh_api.get_vacancies_by_employer(employer_id)
            print(f"Vacancies for {employer}:")
            for vacancy in vacancies:
                print(f"- {vacancy['name']}: {vacancy['alternate_url']}")
        else:
            print(f"No vacancies found for {employer}")