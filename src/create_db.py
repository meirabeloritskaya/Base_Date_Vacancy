import psycopg2
from config import config
from vacancy_api import HeadHunterAPI, employers_vacancies
import os
from dotenv import load_dotenv


def create_database(database_name: str, params: dict):
    """Создание базы данных и таблиц для сохранения данных о компаниях и вакансиях"""

    conn = psycopg2.connect(dbname="postgres", **params)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        cur.execute(f"DROP DATABASE IF EXISTS {database_name}")
    except Exception as e:
        print(f"Информация: {e}")
    finally:
        cur.execute(f"CREATE DATABASE {database_name}")
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


def save_data_to_database(data, database_name, params):
    """Сохранение данных о компаниях и вакансиях в базу данных"""

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
                # employer_id = cur.fetchone()[0]

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
