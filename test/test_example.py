import pytest


def test_equal_or_not_equal():
    assert 3==3

def test_is_instance():
    assert isinstance('this is a string', str)
    assert not isinstance('10', int)

def test_boolean():
    validated= True
    assert validated is True
    assert ("hello"=='world') is False

class Student:
    def __init__(self, first_name: str, last_name: str, major:str, years:int ):
        self.first_name= first_name
        self.last_name= last_name
        self.major= major
        self.years= years

@pytest.fixture

def default_employee():
    return Student('Juan', 'Gonzales', 'Ciencia', 3)

def test_person_initialization(default_employee):
    p= Student('Juan', 'Gonzales', 'Ciencia', 3)
    assert p.first_name== 'Juan', 'Deberia ser Juan'
    assert p.last_name== 'Gonzales', 'Apellido debe ser Gonzales'
    assert p.major == 'Ciencia', 'Deberia ser ciencia'
    assert p.years == 3