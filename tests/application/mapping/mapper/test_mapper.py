import pytest

from application.mapping.mapper import Mapper

from .fixtures import Author, Book, Chapter, Publisher, map_object_to_dict


@pytest.fixture(scope="function")
def book():
    author = Author("Bob")
    publisher = Publisher("Oxford University Press")
    chapters = [Chapter(1), Chapter(2), Chapter(3)]
    return Book(author, publisher, chapters)


@pytest.fixture(scope="function")
def book_json(book):
    return map_object_to_dict(book)


def test_mapper_converts_book_json_into_book_object(book_json):
    book_mapper = Mapper.for_type(Book).with_attribute_mappings(
        author=Mapper.for_type(Author),
        publisher=Mapper.for_type(Publisher),
        chapters=Mapper.for_list_of(Chapter),
    )

    mapped_book = book_mapper.from_json(book_json)

    assert type(mapped_book) == Book
    assert type(mapped_book.author) == Author
    assert type(mapped_book.publisher) == Publisher
    assert type(mapped_book.chapters) == list
    assert type(mapped_book.chapters[0]) == Chapter


def test_type_error_raised_if_for_type_not_given_type():
    with pytest.raises(TypeError) as e:
        _ = Mapper.for_type("str, not a type")

    assert "The target_type argument must be a type (class)." in str(e.value)


def test_type_error_raised_if_for_list_of_not_given_type():
    with pytest.raises(TypeError) as e:
        _ = Mapper.for_list_of("str, not a type")

    assert "The target_type argument must be a type (class)." in str(e.value)


def test_value_error_raised_if_with_attribute_mappings_has_no_arguments():
    with pytest.raises(ValueError) as e:
        _ = Mapper.for_type(Book).with_attribute_mappings()

    assert "No attribute mappings were provided." in str(e.value)


def test_type_error_raised_if_with_attribute_mappings_argument_is_not_Mapper_type():
    with pytest.raises(TypeError) as e:
        _ = Mapper.for_type(Book).with_attribute_mappings(author=Author)

    assert "Required instance of Mapper, received Author" in str(e.value)


@pytest.mark.parametrize("not_a_list", [1, "abc", {"key": "value"}])
def test_value_error_raised_if_list_expected_but_non_list_received(not_a_list, book_json):
    book_mapper = Mapper.for_type(Book).with_attribute_mappings(
        chapters=Mapper.for_list_of(Chapter)
    )
    book_json["chapters"] = not_a_list
    with pytest.raises(ValueError) as e:
        _ = book_mapper.from_json(book_json)

    assert "The mapper was configured to process a list, but" in str(e.value)


@pytest.mark.parametrize("not_a_dict", [1, "abc", ("hi", "bye")])
def test_from_json_raises_TypeError_if_not_provided_with_dict(not_a_dict):
    with pytest.raises(TypeError):
        Mapper().from_json(not_a_dict)
