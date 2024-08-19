import os
from dotenv import load_dotenv
from src.vacancy_api import HeadHunterAPI, employers_vacancies
from src.create_db import create_database, save_data_to_database
from src.manager_db import VacanciesManager
from src.config import config


def main():
    load_dotenv()
    MY_BASE_URL = os.getenv("BASE_URL")
    hh_api = HeadHunterAPI(MY_BASE_URL)
    my_database_name = "vacancy_hh"
    my_params = config()
    employer_ids = [561525, 1721871, 10438139, 9740285, 4667763, 985552, 2628254, 8932785, 1178077, 1455]
    data_vacancies = employers_vacancies(hh_api, employer_ids, per_page=50)

    create_database(my_database_name, my_params)
    save_data_to_database(data_vacancies, "vacancy_hh", my_params)

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
