"""
person.py

Base class for every person in the World Cup System.

Author : Hussain
Project : FIFA World Cup 2026 Management System
"""


class Person:
    """
    Base class of the project.

    Every Player, Coach, Referee and Staff
    inherits from this class.
    """

    def __init__(
        self,
        person_id: int,
        first_name: str,
        last_name: str,
        age: int,
        nationality: str,
        height: float,
        weight: float,
    ):

        self.person_id = person_id
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.nationality = nationality
        self.height = height
        self.weight = weight

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def introduce(self):

        print(f"Hello, I am {self.full_name}.")

    def walk(self):

        print(f"{self.full_name} is walking.")

    def run(self):

        print(f"{self.full_name} is running.")

    def show_info(self):

        print("=" * 50)
        print("PERSON INFORMATION")
        print("=" * 50)

        print(f"ID           : {self.person_id}")
        print(f"Full Name    : {self.full_name}")
        print(f"Age          : {self.age}")
        print(f"Nationality  : {self.nationality}")
        print(f"Height       : {self.height} cm")
        print(f"Weight       : {self.weight} kg")

        print("=" * 50)

    def __str__(self):

        return self.full_name