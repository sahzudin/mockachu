from abc import ABC, abstractmethod
from enum import Enum
from ..localization.manager import get_string


class Generator(ABC):
    """Abstract base class for all data generators.
    
    This class defines the interface that all generators must implement
    to provide data generation capabilities for the mock data generator.
    """
    
    @abstractmethod
    def get_actions(self):
        """Get the list of actions supported by this generator.
        
        Returns:
            list: List of GeneratorActions that this generator supports
        """
        pass

    @abstractmethod
    def get_keys(self):
        """Get the list of keys that this generator can provide.
        
        Returns:
            list: List of string keys that represent the data fields
        """
        pass

    @abstractmethod
    def get_parameters(self, action):
        """Get the list of parameters required for a specific action.
        
        Args:
            action: The GeneratorAction to get parameters for
            
        Returns:
            list: List of parameter names required for the action
        """
        pass

    @abstractmethod
    def generate(self, action, *args):
        """Generate data based on the specified action and parameters.
        
        Args:
            action: The GeneratorAction to perform
            *args: Variable arguments for the generation process
            
        Returns:
            Generated data based on the action and parameters
        """
        pass

    def get_pattern_example(self, action):
        """Get an example pattern for the specified action.
        
        Args:
            action: The GeneratorAction to get a pattern example for
            
        Returns:
            str: Example pattern string
        """
        return "Enter pattern..."

    def args_empty(self, args):
        """Check if the provided arguments are empty.
        
        Args:
            args: Arguments to check
            
        Returns:
            bool: True if args are empty, False otherwise
        """
        if args is not None and len(args) > 0:
            return False
        else:
            return True

    def get_generator_display_name(self, generator_type):
        """Get the localized display name for a generator type.
        
        Args:
            generator_type: The generator type enum
            
        Returns:
            str: Localized display name or formatted fallback
        """
        try:
            return get_string(f"generators.display_names.{generator_type.name}")
        except:
            # Fallback to formatted name if localization key doesn't exist
            return generator_type.name.replace('_', ' ').title()

    def get_action_display_name(self, action):
        """Get the localized display name for an action.
        
        Args:
            action: The action enum
            
        Returns:
            str: Localized display name or formatted fallback
        """
        try:
            return get_string(f"actions.display_names.{action.name}")
        except:
            # Fallback to formatted name if localization key doesn't exist
            return action.name.replace('_', ' ').title()

    def get_parameter_display_name(self, parameter):
        """Get the localized display name for a parameter.
        
        Args:
            parameter: The parameter enum
            
        Returns:
            str: Localized display name or formatted fallback
        """
        try:
            return get_string(f"parameters.display_names.{parameter.name}")
        except:
            # Fallback to formatted name if localization key doesn't exist
            return parameter.name.replace('_', ' ').title()


class Generators(Enum):
    """Enumeration of all available generator types.
    
    Each generator type represents a different category of data generation
    capabilities (e.g., person data, geographic data, etc.).
    """
    BIOLOGY_GENERATOR = 1
    CAR_GENERATOR = 3
    COLOR_GENERATOR = 4
    FILE_GENERATOR = 6
    GEO_GENERATOR = 7
    IT_GENERATOR = 8
    MONEY_GENERATOR = 9
    CINEMA_GENERATOR = 10
    YES_NO_GENERATOR = 12
    STRING_GENERATOR = 13
    PERSON_GENERATOR = 14
    CALENDAR_GENERATOR = 15
    SEQUENCE_GENERATOR = 16
    CUSTOM_LIST_GENERATOR = 17
    FIELD_BUILDER_GENERATOR = 18


class GeneratorActionParameters(Enum):
    """Enumeration of parameter types used by generator actions.
    
    These parameters define the input requirements for various
    generator actions (e.g., length, date ranges, patterns, etc.).
    """
    LENGTH = 1
    PATTERN = 2
    START_DATE = 3
    END_DATE = 4
    START_TIME = 5
    END_TIME = 6
    START_TIMESTAMP = 7
    END_TIMESTAMP = 8
    COUNTRY = 9
    ISO_CODE_2 = 10
    ISO_CODE_3 = 11
    START_RANGE = 12
    END_RANGE = 13
    CARD_BRAND = 14
    START_SEQUENCE = 15
    INTERVAL_SEQUENCE = 16
    DATE_FORMAT = 17
    TIME_FORMAT = 18
    DATETIME_FORMAT = 19
    CUSTOM_LIST = 20
    COUNTRIES_LIST = 21
    PRECISION = 22


class GeneratorActions(Enum):
    """Enumeration of all available generator actions.
    
    Each action represents a specific type of data generation that can be
    performed by generators (e.g., random names, addresses, numbers, etc.).
    Actions are organized by category for better maintainability.
    """
    
    # Biology Generator Actions (1-2)
    RANDOM_ANIMAL = 1
    RANDOM_PLANT = 2
    
    # Car Generator Actions (4-8)
    RANDOM_CAR_BRAND_AND_MODEL = 4
    RANDOM_CAR_BRAND = 5
    RANDOM_CAR_MODEL = 6
    RANDOM_CAR_MODEL_PATTERN = 7
    RANDOM_CAR_VIN = 8
    
    # Color Generator Actions (9-16)
    RANDOM_COMMON_COLOR = 9
    RANDOM_COMMON_COLOR_HEX = 10
    RANDOM_COMMON_COLOR_WITH_HEX = 11
    RANDOM_COMMON_COLOR_PATTERN = 12
    RANDOM_HTML_COLOR = 13
    RANDOM_HTML_COLOR_HEX = 14
    RANDOM_HTML_COLOR_WITH_HEX = 15
    RANDOM_HTML_COLOR_PATTERN = 16
    
    # File Generator Actions (17-19)
    RANDOM_FILE_NAME = 17
    RANDOM_FILE_EXTENSION = 18
    RANDOM_MIME_TYPE = 19
    
    # Geo Generator Actions (20-27)
    RANDOM_TIMEZONE = 20
    RANDOM_GEO_DATA = 21
    RANDOM_CITY = 22
    RANDOM_COUNTRY = 23
    RANDOM_CITY_BY_COUNTRY = 24
    RANDOM_COUNTRY_ISO_CODE_2 = 25
    RANDOM_COUNTRY_ISO_CODE_3 = 26
    RANDOM_GEO_DATA_PATTERN = 27
    
    # IT Generator Actions (28-46)
    RANDOM_IPV4 = 28
    RANDOM_PRIVATE_IPV4 = 29
    RANDOM_PUBLIC_IPV4 = 30
    RANDOM_IPV6 = 31
    RANDOM_MAC_ADDRESS = 32
    RANDOM_DOMAIN = 33
    RANDOM_URL = 34
    RANDOM_KNOWN_URL = 35
    RANDOM_UUID_UPPERCASE = 36
    RANDOM_UUID_LOWERCASE = 37
    RANDOM_ULID = 38
    RANDOM_MD5 = 39
    RANDOM_SHA1 = 40
    RANDOM_SHA256 = 41
    RANDOM_SHA512 = 42
    RANDOM_MONGODB_OBJECT_ID = 43
    RANDOM_EMAIL = 44
    RANDOM_PHONE_NUMBER = 45
    RANDOM_USERNAME = 46
    
    # Money Generator Actions (48-58)
    RANDOM_CURRENCY_AND_CODE = 48
    RANDOM_CURRENCY_NAME = 49
    RANDOM_CURRENCY_CODE = 50
    RANDOM_CURRENCY_PATTERN = 51
    RANDOM_CREDIT_CARD_NUMBER = 52
    RANDOM_CREDIT_CARD_NUMBER_BY_BRAND = 53
    RANDOM_CREDIT_CARD_BRAND = 54
    RANDOM_IBAN = 55
    RANDOM_CVV = 56
    RANDOM_EXPIRY_DATE = 57
    RANDOM_BANK = 58
    
    # Cinema Generator Actions (59-60)
    RANDOM_MOVIE = 59
    RANDOM_SERIE = 60
    
    # Yes/No Generator Actions (61-64)
    RANDOM_BOOLEAN = 61
    RANDOM_BIT = 62
    RANDOM_YES_NO = 63
    RANDOM_Y_N = 64
    
    # String Generator Actions (65-75, 93-94)
    RANDOM_SENTENCE = 65
    RANDOM_WORD = 66
    RANDOM_NUMERIC_STRING_FROM_LENGTH = 67
    RANDOM_NUMERIC_STRING_FROM_RANGE = 68
    RANDOM_ALPHABETICAL_LOWERCASE_STRING = 69
    RANDOM_ALPHABETICAL_UPPERCASE_STRING = 70
    RANDOM_ALPHABETICAL_UPPERCASE_LOWERCASE_STRING = 71
    RANDOM_ALPHANUMERICAL_LOWERCASE_STRING = 72
    RANDOM_ALPHANUMERICAL_UPPERCASE_STRING = 73
    RANDOM_ALPHANUMERICAL_UPPERCASE_LOWERCASE_STRING = 74
    RANDOM_ISBN = 75
    RANDOM_NUMBER = 93
    RANDOM_DECIMAL_NUMBER = 94
    
    # Person Generator Actions (76-84)
    RANDOM_PERSON_GENDER = 76
    RANDOM_PERSON_FIRST_NAME = 77
    RANDOM_PERSON_LAST_NAME = 78
    RANDOM_PERSON_FULL_NAME = 79
    RANDOM_PERSON_EMAIL_FROM_NAME = 80
    RANDOM_PERSON_USERNAME_FROM_NAME = 81
    RANDOM_PERSON_AGE = 82
    RANDOM_PERSON_WEIGHT = 83
    RANDOM_PERSON_HEIGHT = 84
    
    # Calendar Generator Actions (85-88)
    RANDOM_DATE = 85
    RANDOM_TIME = 86
    RANDOM_DATE_TIME = 87
    RANDOM_UNIX_TIMESTAMP = 88
    
    # Sequence Generator Actions (89)
    SEQUENTIAL_NUMBER = 89
    
    # Custom List Generator Actions (90-91)
    RANDOM_CUSTOM_LIST_ITEM = 90
    SEQUENTIAL_CUSTOM_LIST_ITEM = 91
    
    # Field Builder Generator Actions (92)
    FIELD_JOIN = 92


class GeneratorActionParameters(Enum):
    LENGTH = 1
    PATTERN = 2
    START_DATE = 3
    END_DATE = 4
    START_TIME = 5
    END_TIME = 6
    START_TIMESTAMP = 7
    END_TIMESTAMP = 8
    COUNTRY = 9
    ISO_CODE_2 = 10
    ISO_CODE_3 = 11
    START_RANGE = 12
    END_RANGE = 13
    CARD_BRAND = 14
    START_SEQUENCE = 15
    INTERVAL_SEQUENCE = 16
    DATE_FORMAT = 17
    TIME_FORMAT = 18
    DATETIME_FORMAT = 19
    CUSTOM_LIST = 20
    COUNTRIES_LIST = 21
    PRECISION = 22


class GeneratorFormats(Enum):
    """Enumeration of supported output formats for generated data.
    
    Each format represents a different way to structure and export
    the generated mock data (e.g., CSV files, JSON objects, SQL statements).
    """
    JSON = 1
    XML = 2
    CSV = 3
    SQL = 4
    HTML = 5
