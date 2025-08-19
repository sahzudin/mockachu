from .generator import Generator, GeneratorActionParameters, GeneratorActions
from random import choice, randint, uniform
from ..services.file_reader import read_resource_file, read_resource_file_lines


class StringNumberGenerator(Generator):
    """Generator for string and numeric mock data.
    
    Provides generation of various string and numeric data including sentences,
    words, numeric strings, alphabetical strings, alphanumeric strings, ISBN numbers,
    and random numbers. Supports both exact length and range-based generation.
    """
    
    def get_actions(self):
        """Get the list of supported generator actions.
        
        Returns:
            list: List of GeneratorActions for string and numeric data generation
        """
        return [
            GeneratorActions.RANDOM_SENTENCE,
            GeneratorActions.RANDOM_WORD,
            GeneratorActions.RANDOM_NUMERIC_STRING_FROM_LENGTH,
            GeneratorActions.RANDOM_NUMERIC_STRING_FROM_RANGE,
            GeneratorActions.RANDOM_ALPHABETICAL_LOWERCASE_STRING,
            GeneratorActions.RANDOM_ALPHABETICAL_UPPERCASE_STRING,
            GeneratorActions.RANDOM_ALPHABETICAL_UPPERCASE_LOWERCASE_STRING,
            GeneratorActions.RANDOM_ALPHANUMERICAL_LOWERCASE_STRING,
            GeneratorActions.RANDOM_ALPHANUMERICAL_UPPERCASE_STRING,
            GeneratorActions.RANDOM_ALPHANUMERICAL_UPPERCASE_LOWERCASE_STRING,
            GeneratorActions.RANDOM_ISBN,
            GeneratorActions.RANDOM_NUMBER,
            GeneratorActions.RANDOM_DECIMAL_NUMBER
        ]

    def get_parameters(self, action):
        """Get the parameters required for a specific action.
        
        Args:
            action (GeneratorActions): The action to get parameters for
            
        Returns:
            list: List of required parameters for the action
        """
        match action:
            case GeneratorActions.RANDOM_NUMERIC_STRING_FROM_LENGTH:
                return [GeneratorActionParameters.LENGTH.name]
            case GeneratorActions.RANDOM_NUMERIC_STRING_FROM_RANGE:
                return [GeneratorActionParameters.START_RANGE.name, GeneratorActionParameters.END_RANGE.name]
            case GeneratorActions.RANDOM_ALPHABETICAL_LOWERCASE_STRING:
                return [GeneratorActionParameters.LENGTH.name]
            case GeneratorActions.RANDOM_ALPHABETICAL_UPPERCASE_STRING:
                return [GeneratorActionParameters.LENGTH.name]
            case GeneratorActions.RANDOM_ALPHABETICAL_UPPERCASE_LOWERCASE_STRING:
                return [GeneratorActionParameters.LENGTH.name]
            case GeneratorActions.RANDOM_ALPHANUMERICAL_LOWERCASE_STRING:
                return [GeneratorActionParameters.LENGTH.name]
            case GeneratorActions.RANDOM_ALPHANUMERICAL_UPPERCASE_STRING:
                return [GeneratorActionParameters.LENGTH.name]
            case GeneratorActions.RANDOM_ALPHANUMERICAL_UPPERCASE_LOWERCASE_STRING:
                return [GeneratorActionParameters.LENGTH.name]
            case GeneratorActions.RANDOM_NUMBER:
                return [GeneratorActionParameters.START_RANGE.name, GeneratorActionParameters.END_RANGE.name]
            case GeneratorActions.RANDOM_DECIMAL_NUMBER:
                return [GeneratorActionParameters.START_RANGE.name, GeneratorActionParameters.END_RANGE.name, GeneratorActionParameters.PRECISION.name]
        return []

    def get_keys(self):
        """Get the data keys that this generator can produce.
        
        Returns:
            list: List of data keys from parent class
        """
        return super().get_keys()

    def generate(self, action, *args):
        """Generate string or numeric data based on the specified action.
        
        Args:
            action (GeneratorActions): The type of string/numeric data to generate
            *args: Parameters for generation (length, range, precision)
            
        Returns:
            str, int, or float: Generated string or numeric data
        """
        match action:
            case GeneratorActions.RANDOM_SENTENCE:
                return self.__generate_random_sentence()
            case GeneratorActions.RANDOM_WORD:
                return self.__generate_random_word()
            case GeneratorActions.RANDOM_NUMERIC_STRING_FROM_LENGTH:
                return self.__generate_random_numeric_string_from_length() if super().args_empty(args) else self.__generate_random_numeric_string_from_length(args[0])
            case GeneratorActions.RANDOM_NUMERIC_STRING_FROM_RANGE:
                return self.__generate_random_numeric_string_from_range() if super().args_empty(args) else self.__generate_random_numeric_string_from_range(args[0], args[1])
            case GeneratorActions.RANDOM_ALPHABETICAL_LOWERCASE_STRING:
                return self.__generate_random_alphabetical_lowercase_string() if super().args_empty(args) else self.__generate_random_alphabetical_lowercase_string(args[0])
            case GeneratorActions.RANDOM_ALPHABETICAL_UPPERCASE_STRING:
                return self.__generate_random_alphabetical_uppercase_string() if super().args_empty(args) else self.__generate_random_alphabetical_uppercase_string(args[0])
            case GeneratorActions.RANDOM_ALPHABETICAL_UPPERCASE_LOWERCASE_STRING:
                return self.__generate_random_alphabetical_uppercase_lowercase_string() if super().args_empty(args) else self.__generate_random_alphabetical_uppercase_lowercase_string(args[0])
            case GeneratorActions.RANDOM_ALPHANUMERICAL_LOWERCASE_STRING:
                return self.__generate_random_alphanumerical_lowercase_string() if super().args_empty(args) else self.__generate_random_alphanumerical_lowercase_string(args[0])
            case GeneratorActions.RANDOM_ALPHANUMERICAL_UPPERCASE_STRING:
                return self.__generate_random_alphanumerical_uppercase_string() if super().args_empty(args) else self.__generate_random_alphanumerical_uppercase_string(args[0])
            case GeneratorActions.RANDOM_ALPHANUMERICAL_UPPERCASE_LOWERCASE_STRING:
                return self.__generate_random_alphanumerical_uppercase_lowercase_string() if super().args_empty(args) else self.__generate_random_alphanumerical_uppercase_lowercase_string(args[0])
            case GeneratorActions.RANDOM_ISBN:
                return self.__generate_random_isbn()
            case GeneratorActions.RANDOM_NUMBER:
                return self.__generate_random_number() if super().args_empty(args) else self.__generate_random_number(args[0], args[1])
            case GeneratorActions.RANDOM_DECIMAL_NUMBER:
                return self.__generate_random_decimal_number() if super().args_empty(args) else self.__generate_random_decimal_number(args[0], args[1], args[2] if len(args) > 2 else 2)

    __random_sentences = []
    __random_words = []
    __alphabet_lowercase_letters = ""
    __alphabet_lowercase_letters_count = 0
    __alphabet_uppercase_letters = ""
    __alphabet_uppercase_letters_count = 0
    __alphabet_uppercase_lowercase_letters = ""
    __alphabet_uppercase_lowercase_letters_count = 0
    __alphanum_lowercase_letters = ""
    __alphanum_lowercase_letters_count = 0
    __alphanum_uppercase_letters = ""
    __alphanum_uppercase_letters_count = 0
    __alphanum_uppercase_lowercase_letters = ""
    __alphanum_uppercase_lowercase_letters_count = 0
    __numbers_letters_count = 0
    __numbers_letters = ""

    def __init__(self) -> None:
        self.__random_sentences = read_resource_file_lines("sentences.txt")
        self.__alphabet_lowercase_letters = read_resource_file(
            "alphabet_lowercase_string.txt")
        self.__alphabet_lowercase_letters_count = len(
            self.__alphabet_lowercase_letters)

        self.__alphabet_uppercase_letters = read_resource_file(
            "alphabet_uppercase_string.txt")
        self.__alphabet_uppercase_letters_count = len(
            self.__alphabet_uppercase_letters)

        self.__alphabet_uppercase_lowercase_letters = read_resource_file(
            "alphabet_uppercase_lowercase_string.txt")
        self.__alphabet_uppercase_lowercase_letters_count = len(
            self.__alphabet_uppercase_lowercase_letters)

        self.__alphanum_lowercase_letters = read_resource_file(
            "alphanum_lowercase_string.txt")
        self.__alphanum_lowercase_letters_count = len(
            self.__alphanum_lowercase_letters)

        self.__alphanum_uppercase_letters = read_resource_file(
            "alphanum_uppercase_string.txt")
        self.__alphanum_uppercase_letters_count = len(
            self.__alphanum_uppercase_letters)

        self.__alphanum_uppercase_lowercase_letters = read_resource_file(
            "alphanum_uppercase_lowercase_string.txt")
        self.__alphanum_uppercase_lowercase_letters_count = len(
            self.__alphanum_uppercase_lowercase_letters)

        self.__numbers_letters = read_resource_file(
            "numbers.txt")
        self.__numbers_letters_count = len(self.__numbers_letters)

        self.__random_words = read_resource_file_lines(
            "words.txt")

    def __generate_random_sentence(self):
        return choice(self.__random_sentences)

    def __generate_random_word(self):
        return choice(self.__random_words)

    def __generate_random_numeric_string_from_length(self, length=10):
        start_index = randint(
            0, self.__numbers_letters_count - length)
        return self.__numbers_letters[start_index:start_index + length]

    def __generate_random_numeric_string_from_range(self, start_range=1000, end_range=9999):
        random_digits = [str(randint(start_range, end_range))]
        return ''.join(random_digits)

    def __generate_random_alphabetical_lowercase_string(self, length=10):
        start_index = randint(
            0, self.__alphabet_lowercase_letters_count - length)
        return self.__alphabet_lowercase_letters[start_index:start_index + length]

    def __generate_random_alphabetical_uppercase_string(self, length=10):
        start_index = randint(
            0, self.__alphabet_uppercase_letters_count - length)
        return self.__alphabet_uppercase_letters[start_index:start_index + length]

    def __generate_random_alphabetical_uppercase_lowercase_string(self, length=10):
        start_index = randint(
            0, self.__alphabet_uppercase_lowercase_letters_count - length)
        return self.__alphabet_uppercase_lowercase_letters[start_index:start_index + length]

    def __generate_random_alphanumerical_lowercase_string(self, length=10):
        start_index = randint(
            0, self.__alphanum_lowercase_letters_count - length)
        return self.__alphanum_lowercase_letters[start_index:start_index + length]

    def __generate_random_alphanumerical_uppercase_string(self, length=10):
        start_index = randint(
            0, self.__alphanum_uppercase_letters_count - length)
        return self.__alphanum_uppercase_letters[start_index:start_index + length]

    def __generate_random_alphanumerical_uppercase_lowercase_string(self, length=10):
        start_index = randint(
            0, self.__alphanum_uppercase_lowercase_letters_count - length)
        return self.__alphanum_uppercase_lowercase_letters[start_index:start_index + length]

    def __generate_random_isbn(self):
        group_identifier = randint(0, 9)
        publisher_code = randint(0, 99999)
        title_code = randint(0, 999)
        check_digit = randint(0, 9)
        return f"{group_identifier}-{publisher_code:05d}-{title_code:03d}-{check_digit}"

    def __generate_random_number(self, start_range=0, end_range=1000):
        """Generate a random integer within the specified range (can be negative)"""
        return randint(int(start_range), int(end_range))

    def __generate_random_decimal_number(self, start_range=0, end_range=1000, precision=2):
        """Generate a random decimal number within the specified range with given precision"""
        # Generate random float within range
        random_float = uniform(float(start_range), float(end_range))
        # Round to specified precision
        if int(precision) == 0:
            # Return integer when precision is 0
            return int(round(random_float))
        else:
            return round(random_float, int(precision))
