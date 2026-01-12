import pytest

from badcode.bad import add_numbers

 # Assuming add_numbers is in 'your_module.py'

def test_add_two_positive_numbers():
    """Test adding two positive integers."""
    num1 = 5
    num2 = 3
    expected_sum = 8
    actual_sum = add_numbers(num1, num2)
    assert actual_sum == expected_sum, f"Expected {num1} + {num2} to be {expected_sum}, but got {actual_sum}"

def test_add_positive_and_negative_number():
    """Test adding a positive and a negative integer."""
    num1 = 10
    num2 = -3
    expected_sum = 7
    actual_sum = add_numbers(num1, num2)
    assert actual_sum == expected_sum, f"Expected {num1} + {num2} to be {expected_sum}, but got {actual_sum}"

def test_add_two_negative_numbers():
    """Test adding two negative integers."""
    num1 = -7
    num2 = -5
    expected_sum = -12
    actual_sum = add_numbers(num1, num2)
    assert actual_sum == expected_sum, f"Expected {num1} + {num2} to be {expected_sum}, but got {actual_sum}"

def test_add_with_zero_as_first_number():
    """Test adding zero to a positive number."""
    num1 = 0
    num2 = 8
    expected_sum = 8
    actual_sum = add_numbers(num1, num2)
    assert actual_sum == expected_sum, f"Expected {num1} + {num2} to be {expected_sum}, but got {actual_sum}"

def test_add_with_zero_as_second_number():
    """Test adding a negative number to zero."""
    num1 = -15
    num2 = 0
    expected_sum = -15
    actual_sum = add_numbers(num1, num2)
    assert actual_sum == expected_sum, f"Expected {num1} + {num2} to be {expected_sum}, but got {actual_sum}"
