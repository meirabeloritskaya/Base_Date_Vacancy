from abc import ABC, abstractmethod
import psycopg2
from src.config import config


class DBManager(ABC):
    """абстрактный класс для работы с базой данных"""

    @abstractmethod
    def get_companies_and_vacancies_count(self):
        pass

    @abstractmethod
    def get_all_vacancies(self):
        pass

    @abstractmethod
    def get_avg_salary(self):
        pass

    @abstractmethod
    def get_vacancies_with_higher_salary(self):
        pass

    @abstractmethod
    def get_vacancies_with_keyword(self):
        pass


class VacanciesManager(DBManager):
    """класс для получения информации по таблицам из БД vacancy_hh"""

    def __init__(self, database_name, db_params):
        self.conn = psycopg2.connect(dbname=database_name, **db_params)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()

    def get_companies_and_vacancies_count(self):
        """получение информации по количеству вакансий у каждого работодателя"""
        self.cur.execute(
            """
            SELECT e.employer_name, COUNT(v.vacancy_name)
            FROM employers e
            JOIN vacancies v 
            ON e.employer_id = v.employer_id
            GROUP BY e.employer_name
        """
        )
        return self.cur.fetchall()

    def get_all_vacancies(self):
        """получение всей информации по вакансиям"""
        self.cur.execute(
            """
            SELECT v.vacancy_name, v.vacancy_salary, v.salary_currency, v.vacancy_link, e.employer_name 
            FROM vacancies v 
            JOIN employers e ON v.employer_id = e.employer_id
        """
        )
        return self.cur.fetchall()

    def get_avg_salary(self):
        """получение средней зарплаты по вакансиям"""
        self.cur.execute(
            """
            SELECT AVG(vacancy_salary)
            FROM vacancies
            WHERE vacancy_salary IS NOT NULL
        """
        )
        average_salary = self.cur.fetchone()[0]
        return round(average_salary, 2) if average_salary is not None else 0.00

    def get_vacancies_with_higher_salary(self):
        """получение вакансий с зарплатой выше средней"""
        avg_salary = self.get_avg_salary()
        self.cur.execute(
            """
            SELECT v.vacancy_name, v.vacancy_salary, v.salary_currency, v.vacancy_link, e.employer_name
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE v.vacancy_salary > %s
        """,
            (avg_salary,),
        )
        return self.cur.fetchall()

    def get_vacancies_with_keyword(self, keyword):
        """получение вакансий по ключевому слову"""
        lower_keyword = keyword.lower()
        upper_keyword = keyword.upper()
        self.cur.execute(
            """
            SELECT v.vacancy_name, v.vacancy_salary, v.salary_currency, v.vacancy_link, e.employer_name
            FROM vacancies v 
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE LOWER(v.vacancy_name) LIKE %s OR UPPER(v.vacancy_name) LIKE %s
        """,
            (f"%{lower_keyword}%", f"%{upper_keyword}%"),
        )
        return self.cur.fetchall()

    def close_connection(self):
        """закрытие соединения с базой данных"""
        self.cur.close()
        self.conn.close()


if __name__ == "__main__":
    my_database_name = "vacancy_hh"
    db_params = config()
    manager = VacanciesManager(my_database_name, db_params)
    print("Компании и количество вакансий:")
    print(manager.get_companies_and_vacancies_count())

    print("Все вакансии:")
    print(manager.get_all_vacancies())

    print("Средняя зарплата:")
    average_salary = manager.get_avg_salary()
    print(f"{average_salary:.2f}")

    print("Вакансии с зарплатой выше средней:")
    print(manager.get_vacancies_with_higher_salary())

    my_keyword = input("Введите слово для поиска вакансий: ").strip()
    print(f"Вакансии с ключевым словом '{my_keyword}':")
    vacancies = manager.get_vacancies_with_keyword(my_keyword)
    if vacancies:
        for vacancy in vacancies:
            print(vacancy)
    else:
        print(f"Вакансий с ключевым словом '{my_keyword}' не найдено.")
    manager.close_connection()
