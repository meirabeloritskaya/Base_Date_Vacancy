import os
from dotenv import load_dotenv
from src.vacancy_api import HeadHunterAPI, employers_vacancies
from src.create_db import PostgresDatabase
from src.manager_db import VacanciesManager
from src.config import config


def main():
    load_dotenv()
    my_base_url = os.getenv("BASE_URL")
    hh_api = HeadHunterAPI(my_base_url)
    my_database_name = "vacancy_hh"
    my_params = config()

    my_employer_ids = [int(id) for id in os.getenv("EMPLOYER_IDS").split(",")]
    data_vacancies = employers_vacancies(hh_api, my_employer_ids, per_page=50)

    db_vacancy_hh = PostgresDatabase(my_params)
    db_vacancy_hh.create_database(my_database_name)
    db_vacancy_hh.create_tables(my_database_name)
    db_vacancy_hh.save_data_to_database(data_vacancies, my_database_name)

    manager = VacanciesManager(my_database_name, my_params)

    print("_____________")
    print()
    print("Компании и количество вакансий:")
    employers_and_vacancies = manager.get_companies_and_vacancies_count()
    for vacancy in employers_and_vacancies:
        print(vacancy)

    print("_____________")
    print()
    print("Все вакансии:")
    all_vacancies = manager.get_all_vacancies()
    for vacancy in all_vacancies:
        print(vacancy)

    print("_____________")
    print()
    print("Средняя зарплата:")
    average_salary = manager.get_avg_salary()
    print(f"{average_salary:.2f}")

    print("_____________")
    print()
    print("Вакансии с зарплатой выше средней:")
    vacancies_more_avg_salary = manager.get_vacancies_with_higher_salary()
    for vacancy in vacancies_more_avg_salary:
        print(vacancy)

    print("_____________")
    print()
    my_keyword = input("Введите слово для поиска вакансий: ").strip()
    print(f"Вакансии с ключевым словом '{my_keyword}':")
    vacancies = manager.get_vacancies_with_keyword(my_keyword)
    if vacancies:
        for vacancy in vacancies:
            print(vacancy)
    else:
        print(f"Вакансий с ключевым словом '{my_keyword}' не найдено.")
    manager.close_connection()


if __name__ == "__main__":
    main()
