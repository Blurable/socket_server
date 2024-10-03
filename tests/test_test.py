import pytest
from unittest import mock

@pytest.fixture()
def f_wrapper_function(request):
    '''fixture: Возвращает объект'''
    print('\n>', 'fixture: Запуск обертки f_wrapper_function()')
    print('fixture: Создание объекта')
    data = 'Объект из fixture: {}'.format(request.param)
    yield data
    print('fixture: Завершение созданного объекта')
    print('>', 'fixture: Завершение обертки f_wrapper_function()')


@pytest.mark.parametrize('f_wrapper_function', ('параметр 1', 'параметр 2'), indirect=True)
def test_1(f_wrapper_function):
    print('TestSuite: Запуск test1')
    print(f_wrapper_function)
    assert True

@pytest.mark.parametrize('f_wrapper_function', ('параметр 3', 'параметр 4'), indirect=True)
def test_2(f_wrapper_function):
    print('TestSuite: Запуск test2')
    print(f_wrapper_function)
    assert True