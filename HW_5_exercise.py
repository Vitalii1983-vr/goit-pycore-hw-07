import sys
from pathlib import Path
from collections import UserDict
import re
from datetime import datetime, timedelta

# Валідація вводу та обробка помилок


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            return "Не достатньо аргументів. Будь ласка, дотримуйтесь формату команди."
        except ValueError:
            return "Некоректні дані. Переконайтеся, що ви вводите правильні типи даних."
        except KeyError:
            return "Контакт не знайдено."
    return inner

# Базовий клас для полів запису


class Field:
    def __init__(self, value):
        self.value = value  # Ініціалізація значення поля

    def __str__(self):
        return str(self.value)  # Повертає строкове представлення поля

# Клас для зберігання імені контакту


class Name(Field):
    pass  # Наслідування базових властивостей класу Field

# Клас для зберігання номера телефону з валідацією


class Phone(Field):
    def __init__(self, value):
        if not re.fullmatch(r"\d{10}", value):
            raise ValueError("Номер телефону повинен містити рівно 10 цифр.")
        super().__init__(value)  # Виклик конструктора базового класу

# Клас для зберігання дати народження з валідацією


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, '%d.%m.%Y').date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

# Клас для зберігання інформації про контакт


class Record:
    def __init__(self, name):
        self.name = Name(name)  # Збереження імені як об'єкту класу Name
        self.phones = []  # Ініціалізація списку телефонів
        self.birthday = None  # Ініціалізація дня народження

    def add_phone(self, phone):
        self.phones.append(Phone(phone))  # Додавання нового телефону

    def remove_phone(self, phone_number):
        # Видалення телефону
        self.phones = [
            phone for phone in self.phones if phone.value != phone_number]

    def edit_phone(self, old_number, new_number):
        found = False
        for phone in self.phones:
            if phone.value == old_number:
                phone.value = new_number  # Оновлення номеру телефону
                found = True
                break
        if not found:
            raise ValueError("Номер телефону не знайдено.")

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone  # Пошук телефону за номером
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)  # Додавання дня народження

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        birthday = self.birthday.value.strftime(
            '%d.%m.%Y') if self.birthday else "No birthday"
        return f"Name: {self.name.value}, Phones: {phones}, Birthday: {birthday}"

# Клас для зберігання та управління записами


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record  # Додавання запису

    def find(self, name):
        return self.data.get(name, None)  # Пошук запису за ім'ям

    def delete(self, name):
        if name in self.data:
            del self.data[name]  # Видалення запису
        else:
            raise KeyError("Запис не знайдено.")


# Повертає список контактів, у яких день народження наступає протягом заданої кількості днів від поточної дати.

    def get_upcoming_birthdays(self, days=7):
        today = datetime.today().date()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                birthday = record.birthday.value.replace(year=today.year)
                if today <= birthday <= today + timedelta(days=days):
                    upcoming_birthdays.append(record)
        return upcoming_birthdays

# Функції для обробки команд CLI


def parse_input(user_input):
    cmd, *args = user_input.split()  # Розбір введення на команду та аргументи
    cmd = cmd.strip().lower()  # Нормалізація команди
    return cmd, args


# функції для роботи з контактами в адресній книзі, включаючи додавання, зміну, відображення контактів та днів народження. Кожна функція обробляє можливі помилки, використовуючи декоратор @ input_error

# Додає новий контакт або оновлює існуючий контакт в адресній книзі.
@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

#  Змінює номер телефону для існуючого контакту в адресній книзі.


@input_error
def change_contact(args, book):
    if len(args) != 3:
        raise IndexError("Введіть ім'я, старий телефон і новий телефон.")
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return f"Телефон для {name} оновлено з {old_phone} на {new_phone}."
    else:
        raise KeyError(f"Контакт '{name}' не знайдено.")


# Показує номери телефонів для заданого контакту в адресній книзі.
@input_error
def show_phone(args, book):
    if len(args) != 1:
        raise IndexError("Введіть точно одне ім'я.")
    name = args[0]
    record = book.find(name)
    if record:
        return f"{name}: {'; '.join(phone.value for phone in record.phones)}"
    else:
        raise KeyError(f"Контакт '{name}' не знайдено.")


# Показує всі контакти в адресній книзі.
@input_error
def show_all(book):
    if not book.data:
        return "Контакти відсутні."
    return "\n".join(str(record) for record in book.data.values())


# Додає або оновлює день народження для контакту в адресній книзі.
@input_error
def add_birthday(args, book):
    if len(args) != 2:
        raise IndexError(
            "Please provide a name and a birthday in the format DD.MM.YYYY.")
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday for {name} added as {birthday}."
    else:
        raise KeyError(f"Contact '{name}' not found.")

#  Показує день народження для заданого контакту в адресній книзі.


@input_error
def show_birthday(args, book):
    if len(args) != 1:
        raise IndexError("Please provide a name.")
    name = args[0]
    record = book.find(name)
    if record:
        if record.birthday:
            return f"{name}'s birthday is on {record.birthday.value.strftime('%d.%m.%Y')}."
        else:
            return f"{name} does not have a birthday set."
    else:
        raise KeyError(f"Contact '{name}' not found.")

#  Показує контакти, у яких день народження наступає протягом найближчого тижня.


@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No birthdays in the next week."
    return "\n".join(str(record) for record in upcoming_birthdays)

# Головна функція для запуску програми


def main():
    # Створює новий об'єкт адресної книги
    book = AddressBook()
    print("Welcome to the assistant bot!")  # Вітальне повідомлення

# Основний цикл програми, який триває доти, доки користувач не введе команду для виходу
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)
# Перевіряє, чи команда є командою для виходу з програми
        if command in ["close", "exit"]:
            print("Good bye!")  # Виводить повідомлення про завершення роботи
            break  # Завершує виконання циклу і виходить з програми
# Привітання
        elif command == "hello":
            print("How can I help you?")  # Відповідає на команду "hello"
# Додавання нового контакту
        elif command == "add":
            # Викликає функцію для додавання контакту і виводить результат
            print(add_contact(args, book))
# Зміна існуючого контакту
        elif command == "change":
            print(change_contact(args, book))
# Показати номер телефону для певного контакту
        elif command == "phone":
            print(show_phone(args, book))
# Показати всі контакти
        elif command == "all":
            print(show_all(book))
# Додавання дня народження до контакту
        elif command == "add-birthday":
            print(add_birthday(args, book))
# Показати день народження певного контакту
        elif command == "show-birthday":
            print(show_birthday(args, book))
 # Показати контакти з днями народження, які наступають протягом найближчого тижня
        elif command == "birthdays":
            print(birthdays(args, book))
# Обробка невідомої команди
        else:
            print("Invalid command.")


# Запуск головної функції, якщо скрипт виконується напряму
if __name__ == "__main__":
    main()

# _______________________________________________________________
# # Команди, які може виконувати цей код:
# 1. add[ім'я] [номер телефону] — додає новий контакт або оновлює існуючий.
# 2. change [ім'я] [старий номер телефону] [новий номер телефону] — змінює номер телефону для існуючого контакту.
# 3. phone [ім'я] — показує номери телефонів для заданого імені.
# 4. all — показує всі контакти в адресній книзі.
# 5. add-birthday [ім'я] [день народження] — додає або оновлює день народження для контакту.
# 6. show-birthday [ім'я] — показує день народження для заданого імені.
# 7. birthdays — показує контакти з днями народження, які наступають протягом наступного тижня.
# 8. hello — привітальне повідомлення.
# 9. close, exit — вихід з програми.
