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
    def get_vacancies_by_employer(self, employer_id: int):
        """Получение вакансий по ID работодателя"""
        pass


class HeadHunterAPI(WebsiteAPI):
    """Класс для получения списка вакансий с сайта HeadHunter."""

    def __init__(self, base_url: str):
        """Инициализирует HeadHunterAPI с базовым URL"""
        logger.info("Инициализация HeadHunterAPI с базовым URL")
        self.base_url = base_url
        self.headers = {"User-Agent": "HH-User-Agent"}

    def get_vacancies_by_employer(self, employer_id: int, per_page: int = 10):
        """Получение вакансий по ID работодателя"""

        logger.info(f"Запрос вакансий для работодателя ID {employer_id}")
        vacancies_url = f"{self.base_url}/vacancies"
        params = {"employer_id": employer_id, "per_page": per_page}
        try:
            response = requests.get(url=vacancies_url, headers=self.headers, params=params)
            response.raise_for_status()
            logger.info(f"Запрос успешно выполнен для вакансий работодателя с ID {employer_id}")

            data = response.json()
            return data.get("items", [])

        except requests.RequestException as e:
            logger.error(f"Ошибка запроса к API при получении вакансий: {e}")
            raise


def employers_vacancies(api_instance: HeadHunterAPI, employer_ids: list, per_page: int = 10):
    """Получение вакансии для списка работодателей"""
    logger.info("Начало получения вакансий для списка работодателей")
    all_vacancies = []
    for employer_id in employer_ids:
        logger.info(f"Получение вакансий для работодателя ID {employer_id}")
        vacancies = api_instance.get_vacancies_by_employer(employer_id, per_page)
        all_vacancies.extend(vacancies)
    logger.info("Получение вакансий завершено")
    return all_vacancies


if __name__ == "__main__":
    load_dotenv()
    MY_BASE_URL = os.getenv("BASE_URL")
    hh_api = HeadHunterAPI(MY_BASE_URL)

    # Список работодателей для получения данных
    employer_ids = [561525, 1721871, 10438139, 9740285, 4667763, 985552, 2628254, 8932785, 1178077, 1455]

    my_vacancies = employers_vacancies(hh_api, employer_ids, per_page=50)
    for vacancy in my_vacancies:
        print(vacancy)
