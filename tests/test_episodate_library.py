import pytest
from episodate_library import TVSearchController


@pytest.fixture
def episodate_object():
    return TVSearchController()


def test_search(episodate_object):
    search_term = "Big Brother Canada"
    result = episodate_object.search(search_term)
    print(result)

if __name__ == "__main__":
    print("hello world")