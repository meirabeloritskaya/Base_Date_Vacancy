import logging
import os
from dotenv import load_dotenv
from src.vacancy_api import HeadHunterAPI, fetch_vacancies_for_employers
from create_db import create_database, save_data_to_database
from config import config


def main():
    load_dotenv()
    MY_BASE_URL = os.getenv("BASE_URL")
    hh_api = HeadHunterAPI(MY_BASE_URL)

    # Список работодателей для получения данных
    employer_ids = [561525, 1721871, 10438139, 9740285, 4667763, 985552, 2628254, 8932785, 1178077, 1455]
    data_vacancies = fetch_vacancies_for_employers(hh_api, employer_ids, per_page=50)

    params = config()
    create_database('vacancy_hh', params)

    save_data_to_database(data_vacancies, 'vacancy_hh', params)


if __name__ == '__main__':
    main()