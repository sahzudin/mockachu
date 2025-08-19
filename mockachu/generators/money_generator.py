from .generator import Generator, GeneratorActionParameters, GeneratorActions
from .string_generator import StringNumberGenerator
from random import choice, randint
import datetime

from ..services.file_reader import read_resource_file_json, read_resource_file_lines


class MoneyGenerator(Generator):
    """Generator for money and financial-related mock data.
    
    Provides generation of financial data including currencies, credit card numbers,
    bank information, CVV codes, expiry dates, and IBAN numbers. Supports various
    international currency formats and banking standards.
    """
    
    def get_actions(self):
        """Get the list of supported generator actions.
        
        Returns:
            list: List of GeneratorActions for financial data generation
        """
        return [
            GeneratorActions.RANDOM_CURRENCY_AND_CODE,
            GeneratorActions.RANDOM_CURRENCY_NAME,
            GeneratorActions.RANDOM_CURRENCY_CODE,
            GeneratorActions.RANDOM_CURRENCY_PATTERN,
            GeneratorActions.RANDOM_CREDIT_CARD_NUMBER,
            # GeneratorActions.RANDOM_CREDIT_CARD_NUMBER_BY_BRAND, #now convenient
            GeneratorActions.RANDOM_CREDIT_CARD_BRAND,
            GeneratorActions.RANDOM_IBAN,
            GeneratorActions.RANDOM_CVV,
            GeneratorActions.RANDOM_EXPIRY_DATE,
            GeneratorActions.RANDOM_BANK
        ]

    def get_parameters(self, action):
        """Get the parameters required for a specific action.
        
        Args:
            action (GeneratorActions): The action to get parameters for
            
        Returns:
            list: List of required parameters for the action
        """
        match action:
            case GeneratorActions.RANDOM_CURRENCY_PATTERN:
                return [GeneratorActionParameters.PATTERN.name]
            case GeneratorActions.RANDOM_CREDIT_CARD_NUMBER_BY_BRAND:
                return [GeneratorActionParameters.CARD_BRAND.name]
        return []

    def get_keys(self):
        return ["currency", "code"]

    def get_available_credit_card_brands(self):
        """Get list of available credit card brands for select list"""
        brands = []
        for card in self.__card_types:
            brands.append(card["brand"])
        return sorted(brands)

    def get_pattern_example(self, action):

        match action:
            case GeneratorActions.RANDOM_CURRENCY_PATTERN:
                return "{currency} ({code})"
        return super().get_pattern_example(action)

    def generate(self, action, *args):
        """Generate financial data based on the specified action.
        
        Args:
            action (GeneratorActions): The type of financial data to generate
            *args: Additional arguments (pattern for currency, brand for cards)
            
        Returns:
            str or dict: Generated financial data (currency, card number, IBAN, etc.)
        """
        match action:
            case GeneratorActions.RANDOM_CURRENCY_AND_CODE:
                return self.__get_random_currency_and_code()
            case GeneratorActions.RANDOM_CURRENCY_NAME:
                return self.__get_random_currency_name()
            case GeneratorActions.RANDOM_CURRENCY_CODE:
                return self.__get_random_currency_code()
            case GeneratorActions.RANDOM_CURRENCY_PATTERN:
                return self.__get_radnom_currency_by_patterns() if super().args_empty(args) else self.__get_radnom_currency_by_patterns(args[0])
            case GeneratorActions.RANDOM_CREDIT_CARD_NUMBER:
                return self.__get_random_credit_card_number()
            case GeneratorActions.RANDOM_CREDIT_CARD_NUMBER_BY_BRAND:
                return self.__get_random_credit_card_number_by_brand() if super().args_empty(args) else self.__get_random_credit_card_number_by_brand(args[0])
            case GeneratorActions.RANDOM_CREDIT_CARD_BRAND:
                return self.__get_random_credit_card_brand()
            case GeneratorActions.RANDOM_IBAN:
                return self.__get_random_iban()
            case GeneratorActions.RANDOM_CVV:
                return self.__generate_random_cvv()
            case GeneratorActions.RANDOM_EXPIRY_DATE:
                return self.__get_random_expiry_date()
            case GeneratorActions.RANDOM_BANK:
                return self.__get_random_bank()

    __random_string_generator = None
    __banks = []
    __card_types = []
    __iban_formats = []
    __currencies = []

    def __init__(self) -> None:
        self.__random_string_generator = StringNumberGenerator()
        self.__banks = read_resource_file_lines("banks.txt")
        self.__card_types = read_resource_file_json("bank_card_types.json")
        self.__iban_formats = read_resource_file_json("iban_formats.json")
        self.__currencies = read_resource_file_json("currencies.json")

    def __get_random_currency_and_code(self):
        random_currency = choice(self.__currencies)
        return random_currency["currency"] + " (" + random_currency["code"] + ")"

    def __get_random_currency_name(self):
        random_currency = choice(self.__currencies)
        return random_currency["currency"]

    def __get_random_currency_code(self):
        random_currency = choice(self.__currencies)
        return random_currency["code"]

    def __get_radnom_currency_by_patterns(self, pattern=""):
        random_currency = choice(self.__currencies)
        for key in self.get_keys():
            pattern = str(pattern).replace(
                f"{{{key}}}", str(random_currency[key]))
        return pattern

    def __get_random_credit_card_number(self):
        card = choice(self.__card_types)
        return self.__replace_X_with_random_number(str(choice(card["patterns"])))

    def __get_random_credit_card_number_by_brand(self, brand=None):
        if brand is None:
            brand = self.__get_random_credit_card_brand()
        for card in self.__card_types:
            if card["brand"].lower() == brand.lower():
                return self.__replace_X_with_random_number(str(choice(card["patterns"])))
        return None

    def __get_random_credit_card_brand(self):
        return choice(self.__card_types)["brand"]

    def __get_random_iban(self):
        random_iban_pattern = choice(self.__iban_formats)
        return random_iban_pattern["country_code"] \
            + self.__random_string_generator.generate(GeneratorActions.RANDOM_NUMERIC_STRING_FROM_LENGTH, 2) \
            + self.__random_string_generator.generate(GeneratorActions.RANDOM_ALPHANUMERICAL_UPPERCASE_STRING, 4) \
            + self.__random_string_generator.generate(
                GeneratorActions.RANDOM_NUMERIC_STRING_FROM_LENGTH, random_iban_pattern["length"] - 8)

    def __generate_random_cvv(self):
        return str(randint(100, 999))

    def __get_random_expiry_date(self):
        current_year = datetime.datetime.now().year
        future_year = current_year + randint(1, 10)
        month = randint(1, 12)
        year = future_year % 100  # Get the last two digits of the future year
        expiry_date = f"{month:02d}/{year:02d}"
        return expiry_date

    def __get_random_bank(self):
        return choice(self.__banks)

    def __replace_X_with_random_number(self, pattern):
        return "".join(str(randint(0, 9)) if char == "X" else char for char in pattern)
