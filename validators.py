"""Import regular expressions for validators"""
from datetime import datetime
import re

def validate_season_year(season):
    """Checks if the input data for season is within the specified criteria"""
    is_valid_season = False
    currentyear = datetime.now().year
    while not is_valid_season:
        if season < 1979 or season > currentyear:
            error = f"Date is outside of valid range of 1979-{currentyear}."
            return error
        elif season >= 1979 and season <= currentyear:
            is_valid_season = True
        else:
            break

    return True

def validate_player_name(name):
    """Checks if provided name is of valid format"""
    is_valid_name = False
    try:
        int(name)
        error = "Name cannot be a number."
        return error
    except ValueError:
        name = name.lower()

        while not is_valid_name:
            contains_number = re.search("[0-9]", name)
            is_valid = re.search("[a-zA-Z.]", name)
            if contains_number is not None:
                error = "Names cannot contain numbers. Only latin letters please."
                return error
            elif is_valid is not None:
                is_valid_name = True
            else:
                print(is_valid)
                error = "Name contains non-allowed characters. Only latin letters please."
                return error
            break

        return is_valid_name
