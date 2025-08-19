from .generator import Generator, GeneratorActions
from random import choice, randint
from ..services.file_reader import read_resource_file_lines

class PersonGenerator(Generator):
    """Generator for person-related mock data.
    
    Provides generation of realistic person data including names, demographics,
    and contact information. Maintains consistency within a row for related
    person attributes (e.g., gender-appropriate names, email based on name).
    """
    
    def __init__(self):
        """Initialize the PersonGenerator with name and domain data.
        
        Loads name lists and email domains from resource files and initializes
        row-based person data tracking for consistency.
        """
        self._load_name_data()
        self._current_row_person = None  # Person data for current row
        self._row_initialized = False  # Flag to track if current row person is set

    def _load_name_data(self):
        """Load name and email domain data from resource files.
        
        Loads male names, female names, last names, and email domains
        for use in person generation.
        """
        self.__male_first_names = read_resource_file_lines(
            "male_first_names.txt")
        self.__female_first_names = read_resource_file_lines(
            "female_first_names.txt")
        self.__last_names = read_resource_file_lines("last_names.txt")
        self.__popular_email_domains = read_resource_file_lines(
            "email_domains.txt")

    def get_actions(self):
        """Get the list of supported generator actions.
        
        Returns:
            list: List of GeneratorActions for person data generation
        """
        return [GeneratorActions.RANDOM_PERSON_GENDER,
                GeneratorActions.RANDOM_PERSON_FIRST_NAME,
                GeneratorActions.RANDOM_PERSON_LAST_NAME,
                GeneratorActions.RANDOM_PERSON_FULL_NAME,
                GeneratorActions.RANDOM_PERSON_EMAIL_FROM_NAME,
                GeneratorActions.RANDOM_PERSON_USERNAME_FROM_NAME,
                GeneratorActions.RANDOM_PERSON_AGE,
                GeneratorActions.RANDOM_PERSON_WEIGHT,
                GeneratorActions.RANDOM_PERSON_HEIGHT
                ]

    def get_parameters(self, action):
        return []

    def get_keys(self):
        return ["first_name", "last_name", "full_name", "username", "email", "gender", "age", "weight", "height"]

    def _generate_person_data(self):

        gender = choice(["Male", "Female"])
        first_name = choice(self.__male_first_names) if gender == "Male" else choice(
            self.__female_first_names)
        last_name = choice(self.__last_names)
        full_name = first_name + " " + last_name
        username = str(first_name).lower() + "." + str(last_name).lower()
        email = str(first_name).lower() + "." + \
            str(last_name).lower() + "@" + choice(self.__popular_email_domains)
        age = randint(15, 70)
        height = randint(150, 210)
        weight = randint(55, 120)

        return {
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "username": username,
            "email": email,
            "gender": gender,
            "age": age,
            "weight": weight,
            "height": height
        }

    def _get_current_person(self):

        if not self._row_initialized:
            self._current_row_person = self._generate_person_data()
            self._row_initialized = True
        return self._current_row_person

    def start_new_row(self):

        self._row_initialized = False
        self._current_row_person = None

    def generate(self, action, *args):
        """Generate person data based on the specified action.
        
        Args:
            action (GeneratorActions): The type of person data to generate
            *args: Additional arguments (not used by person generator)
            
        Returns:
            str, int, or float: Generated person data (name, age, contact info, etc.)
        """
        person_data = self._get_current_person()

        match action:
            case GeneratorActions.RANDOM_PERSON_GENDER:
                return person_data["gender"]
            case GeneratorActions.RANDOM_PERSON_FIRST_NAME:
                return person_data["first_name"]
            case GeneratorActions.RANDOM_PERSON_LAST_NAME:
                return person_data["last_name"]
            case GeneratorActions.RANDOM_PERSON_FULL_NAME:
                return person_data["full_name"]
            case GeneratorActions.RANDOM_PERSON_EMAIL_FROM_NAME:
                return person_data["email"]
            case GeneratorActions.RANDOM_PERSON_USERNAME_FROM_NAME:
                return person_data["username"]
            case GeneratorActions.RANDOM_PERSON_AGE:
                return person_data["age"]
            case GeneratorActions.RANDOM_PERSON_WEIGHT:
                return person_data["weight"]
            case GeneratorActions.RANDOM_PERSON_HEIGHT:
                return person_data["height"]
