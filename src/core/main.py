import os
from typing import Dict, List

from src.constants import (
    DRINKS_FILE_PATH,
    PEOPLE_FILE_PATH,
    FAVOURITES_FILE_PATH,
    DRNIKS_MENU_USUAL_OPTION
)
from src.data_store.files import read_lines, save_lines
from src.data_store.file_store import File_Store
from src.models.round import Round
from src.models.person import Person
from src.core.menu import select_from_menu, clear_screen
from src.core.table import print_table
from src.core.input import select_person_from_menu

PERSON_ID_INDEX = 0
PERSON_FIRST_NAME_INDEX = 1
PERSON_LAST_NAME_INDEX = 2
PERSON_DRINK_NAME_INDEX = 3


def load_data(people: list, drinks: list, favourites: dict):
    people_store = File_Store(PEOPLE_FILE_PATH)
    drinks_store = File_Store(DRINKS_FILE_PATH)
    favourites_store = File_Store(FAVOURITES_FILE_PATH)
    # Load people
    for person_data in people_store.read_csv():
        people.append(Person(
            int(person_data[PERSON_ID_INDEX]),
            person_data[PERSON_FIRST_NAME_INDEX],
            person_data[PERSON_LAST_NAME_INDEX],
            person_data[PERSON_DRINK_NAME_INDEX],
            ))
    # Load drinks
    for drink in drinks_store.read_lines():
        drinks.append(drink)
    # Load favourites
    for item in favourites_store.read_lines():
        # Unpacking the items in the list to separate variables
        # https://treyhunner.com/2018/03/tuple-unpacking-improves-python-code-readability/
        # I know items.split will return a list with two items, because of the second argument
        # it will only split once even if there are more instances of ':' in the string
        #
        # https://www.programiz.com/python-programming/methods/string/split
        # https://docs.python.org/3/library/stdtypes.html?highlight=split#str.rsplit
        name, drink = item.split(":", 1)
        valid = True
        if name not in [person.get_full_name() for person in people]:
            valid = False
            print(f'{name} is not a known person')
        if drink not in drinks:
            valid = False
            print(f'{drink} is not a known drink')
        if not valid:
            continue

        favourites[name] = drink


def save_data(people: list, drinks: list, favourites: dict):
    people_store = File_Store(
        PEOPLE_FILE_PATH,
        save_processor=lambda person: person.get_full_name())
    drinks_store = File_Store(DRINKS_FILE_PATH)
    favourites_store = File_Store(FAVOURITES_FILE_PATH)
    # Save people
    people_store.save_to_csv([[person.id, person.first_name, person.last_name, person.drink] for person in people])
    # Save drinks
    drinks_store.save_lines(drinks)
    # Save favourites
    # Defining a consistent structure here so that I can parse/recognise it when loading
    # f'{name}:{drink}'
    # TODO: Save as a CSV?
    favourites_store.save_lines([f'{name}:{drink}' for name, drink in favourites.items()])


def get_available_drinks_for_round(favourites, drinks, name):
    if name in favourites.keys():
        return drinks + [DRNIKS_MENU_USUAL_OPTION]
    else:
        return drinks


def build_round(round: Round, favourites: Dict, people: List[str], drinks: List[str]):
    while True:
        clear_screen()
        round.print_order()
        # Set name, drink and finish to the same value, None
        person = drink = finish = None
        while not person:
            person = select_person_from_menu(
                people, '\nWhose drink would like to set?')
            if not person:
                print("Please choose a number from the menu")

        # If the person has a stored favourite drink add an option to the drinks menu
        available_drinks = get_available_drinks_for_round(
            favourites, drinks, person.get_full_name())

        while not drink:
            index = select_from_menu(
                f'Please choose a drink for {person.get_full_name()}', available_drinks)
            if index is False:
                print("Please choose a number from the menu")
            drink = drinks[index]

        if drink == DRNIKS_MENU_USUAL_OPTION:
            drink = favourites[person.get_full_name()]
        round.add_to_round(favourites, person.get_full_name(), drink=drink)
        clear_screen()

        # Ask to add another order with end round option
        while not finish:
            round.print_order()
            options = ['Yes', 'No']
            index = select_from_menu(
                '\nDo you want to add another drink?', options, clear=False)
            if index is False:
                print("Please choose a number from the menu")
                continue
            if options[index] == "No":
                return round
            break


# Can process a list of any objects with an id property
def get_last_id(people: list) -> int:
    last_id = None
    for person in people:
        print(type(person.id))
        if last_id == None:
            last_id = person.id
            continue
        if last_id < person.id:
            last_id = person.id
    return last_id
