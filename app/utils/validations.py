from rest_framework.exceptions import ValidationError
import re


def is_value_null_or_blank_return_boolean(value, disregard_zeroes_for_numbers=False):
    data_type = type(value)

    if data_type is list:
        return len(value) == 0

    if data_type is str:
        return value == "" or value is None

    if data_type is int or data_type is float:
        if disregard_zeroes_for_numbers:
            return value is None
        else:
            return value == 0 or 0.0 or value is None

    if data_type is list:
        new_list = []

        # Remove all elements that are whitespaces only
        for item in value:
            stripped_item = item.strip()

            if stripped_item:
                new_list.append(item)

        return len(new_list) == 0


def password_validator_throws_exception(
    password,
    old_password=None,
    min_length=8,
    has_digit_checker=False,
    has_capital_letter_checker=False,
    has_special_char_checker=False,
):
    if old_password and password == old_password:
        raise ValidationError({"message": "Password must not match the old password."})

    if len(password) < min_length:
        raise ValidationError(
            {"message": "Password must be at least 8 characters long."}
        )

    if has_digit_checker:
        if not re.search(r"[0-9]", password):
            raise ValidationError(
                {"message": "Password must contain at least one digit."}
            )

    if has_capital_letter_checker:
        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                {"message": "Password must contain at least one uppercase letter."}
            )

    if has_special_char_checker:
        if not re.search(r'[!@#$%^&*(),.?_":{}|<>]', password):
            raise ValidationError(
                {"message": "Password must contain at least one special character."}
            )
