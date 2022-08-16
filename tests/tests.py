# from hermes import Hermes
from bs4 import BeautifulSoup
import pytest

def mock_get_soup(html):
    try:
        with open(html, 'rb') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
    except:
        print('html file does not exist')
    return soup

def test_assert_false():
    assert 1 == 1