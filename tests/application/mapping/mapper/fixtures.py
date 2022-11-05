import json


class Author:
    def __init__(self, name):
        self.name = name


class Publisher:
    def __init__(self, company_name):
        self.company_name = company_name


class Chapter:
    def __init__(self, number):
        self.number = number


class Book:
    def __init__(self, author: Author, publisher: Publisher, chapters: list = []):
        self.author = author
        self.publisher = publisher
        self.chapters = chapters


def map_object_to_dict(obj):
    return json.loads(json.dumps(obj, default=lambda o: getattr(o, "__dict__", str(o))))
