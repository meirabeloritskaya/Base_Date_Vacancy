import psycopg2
from config import config

def create_database(database_name: str, params: dict):
    """Создание базы данных и таблиц для сохранения данных о компаниях и вакансиях"""

    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        cur.execute(f"DROP DATABASE {database_name}")
    except Exception as e:
        print(f'Информация: {e}')
    finally:
        cur.execute(f"CREATE DATABASE {database_name}")

    conn.close()

    with psycopg2.connect(dbname=database_name, **params) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                CREATE TABLE employers(
                id SERIAL PRIMARY KEY NOT NULL,
                employer_id INTEGER NOT NULL,
                employer_name VARCHAR)
                ''')

            with conn.cursor() as cur:
                cur.execute('''
                CREATE TABLE vacancies(
                id SERIAL PRIMARY KEY NOT NULL,
                vacancy_name VARCHAR,
                vacancy_salary INTEGER NOT NULL,
                salary_currency VARCHAR,
                vacancy_link VARCHAR)
                ''')

def save_data_to_database(data, database_name, params):
    '''Сохранение данных о компаниях и вакансиях в базу данных'''

    with psycopg2.connect(dbname=database_name, **params) as conn:
        with conn.cursor as cur:


if __name__ == '__main__':
    params = config()
    create_database('vacancy_hh', params)