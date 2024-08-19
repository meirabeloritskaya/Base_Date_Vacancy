import psycopg2
from src.config import config
from src.vacancy_api import HeadHunterAPI, employers_vacancies
import os
from dotenv import load_dotenv
import logging


logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(BASE_DIR, "logs", "create_db.log")
file_handler = logging.FileHandler(path, encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


def create_database(database_name: str, params: dict):
    """Создание базы данных и таблиц для сохранения данных о компаниях и вакансиях"""

    conn = psycopg2.connect(dbname="postgres", **params)
    conn.autocommit = True
    cur = conn.cursor()
    logger.info(f"Создание базы данных {database_name}")
    try:
        cur.execute(f"DROP DATABASE IF EXISTS {database_name}")
        logger.info(f"База данных {database_name} удалена (если существовала)")
    except Exception as e:
        logger.warning(f"Ошибка при удалении базы данных: {e}")
        print(f"Информация: {e}")
    finally:
        cur.execute(f"CREATE DATABASE {database_name}")
        logger.info(f"База данных {database_name} создана")
        cur.close()
        conn.close()

    with psycopg2.connect(dbname=database_name, **params) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE employers(
                employer_id INTEGER PRIMARY KEY,
                employer_name VARCHAR)
                """
            )
            logger.info("Таблица employers создана")

            cur.execute(
                """
                CREATE TABLE vacancies(
                employer_id INTEGER REFERENCES employers(employer_id),
                vacancy_name VARCHAR,
                vacancy_salary INTEGER,
                salary_currency VARCHAR,
                vacancy_link VARCHAR)
                """
            )
            logger.info("Таблица vacancies создана")


def save_data_to_database(data, database_name, params):
    """Сохранение данных о компаниях и вакансиях в базу данных"""
    logger.info(f"Сохранение данных в базу данных {database_name}")
    with psycopg2.connect(dbname=database_name, **params) as conn:
        with conn.cursor() as cur:
            for vacancy in data:
                cur.execute(
                    """
                    INSERT INTO employers (employer_id, employer_name)
                    VALUES (%s, %s)
                    ON CONFLICT (employer_id) DO NOTHING
                    RETURNING employer_id
                    """,
                    (vacancy["employer"]["id"], vacancy["employer"]["name"]),
                )
                logger.info(f"Данные о работодателе {vacancy['employer']['name']} сохранены")

                cur.execute(
                    """
                            INSERT INTO vacancies (employer_id, vacancy_name, vacancy_salary, salary_currency, vacancy_link)
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                    (
                        vacancy["employer"]["id"],
                        vacancy["name"],
                        vacancy["salary"]["from"] if vacancy["salary"] else None,
                        vacancy["salary"]["currency"] if vacancy["salary"] else None,
                        vacancy["alternate_url"],
                    ),
                )
                logger.info(f"Вакансия {vacancy['name']} сохранена")


if __name__ == "__main__":
    params = config()
    create_database("vacancy_hh", params)
    load_dotenv()
    MY_BASE_URL = os.getenv("BASE_URL")
    hh_api = HeadHunterAPI(MY_BASE_URL)

    # Список работодателей для получения данных
    employer_ids = [561525, 1721871, 10438139, 9740285, 4667763, 985552, 2628254, 8932785, 1178077, 1455]
    vacancies = employers_vacancies(hh_api, employer_ids, per_page=50)

    save_data_to_database(vacancies, "vacancy_hh", params)
