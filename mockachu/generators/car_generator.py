from .generator import Generator, GeneratorActionParameters, GeneratorActions
from random import choice
import string

from ..services.file_reader import read_resource_file_json

class CarGenerator(Generator):
    """Generator for car-related mock data.
    
    Provides generation of car brands, models, VINs, and related automotive data.
    Maintains consistency within a row for related car attributes to ensure
    brand and model combinations are realistic.
    """
    
    def __init__(self) -> None:
        """Initialize the CarGenerator with car data.
        
        Loads car brand and model data from resource files and initializes
        row-based car data tracking for consistency.
        """
        self.__cars = read_resource_file_json("cars.json")
        self._current_row_car = None  # Car data for current row
        self._row_initialized = False  # Flag to track if current row car is set

    def get_actions(self):
        """Get the list of supported generator actions.
        
        Returns:
            list: List of GeneratorActions for car data generation
        """
        return [
            GeneratorActions.RANDOM_CAR_BRAND_AND_MODEL,
            GeneratorActions.RANDOM_CAR_BRAND,
            GeneratorActions.RANDOM_CAR_MODEL,
            GeneratorActions.RANDOM_CAR_MODEL_PATTERN,
            GeneratorActions.RANDOM_CAR_VIN
        ]

    def get_parameters(self, action):
        """Get the parameters required for a specific action.
        
        Args:
            action (GeneratorActions): The action to get parameters for
            
        Returns:
            list: List of required parameters for pattern-based actions
        """
        match action:
            case GeneratorActions.RANDOM_CAR_MODEL_PATTERN:
                return [GeneratorActionParameters.PATTERN.name]
        return []

    def get_keys(self):
        return ["brand", "model", "vin"]

    def get_pattern_example(self, action):

        match action:
            case GeneratorActions.RANDOM_CAR_MODEL_PATTERN:
                return "{brand} {model}"
        return super().get_pattern_example(action)

    def _generate_car_data(self):

        random_car_brand = choice(self.__cars)
        selected_model = choice(random_car_brand["models"])
        generated_vin = self.__generate_random_car_vin()

        return {
            "brand": random_car_brand["brand"],
            "model": selected_model,
            "vin": generated_vin,
            "brand_and_model": random_car_brand["brand"] + ' ' + selected_model
        }

    def _get_current_car(self):

        if not self._row_initialized:
            self._current_row_car = self._generate_car_data()
            self._row_initialized = True
        return self._current_row_car

    def start_new_row(self):

        self._row_initialized = False
        self._current_row_car = None

    def generate(self, action, *args):
        """Generate car-related data based on the specified action.
        
        Args:
            action (GeneratorActions): The type of car data to generate
            *args: Additional arguments (brand for model selection, pattern for formatting)
            
        Returns:
            str: Generated car data (brand, model, VIN, etc.)
        """
        car_data = self._get_current_car()

        match action:
            case GeneratorActions.RANDOM_CAR_BRAND_AND_MODEL:
                return car_data["brand_and_model"]
            case GeneratorActions.RANDOM_CAR_BRAND:
                return car_data["brand"]
            case GeneratorActions.RANDOM_CAR_MODEL:
                if not super().args_empty(args):
                    return self.__get_random_car_model_from_brand(args[0])
                return car_data["model"]
            case GeneratorActions.RANDOM_CAR_MODEL_PATTERN:
                return self.__get_random_car_by_pattern(car_data) if super().args_empty(args) else self.__get_random_car_by_pattern(car_data, args[0])
            case GeneratorActions.RANDOM_CAR_VIN:
                return car_data["vin"]

    __cars = []

    def __get_random_car_model_from_brand(self, brand):

        for car in self.__cars:
            if car["brand"].lower() == brand.lower():
                return choice(car["models"])
        return self._get_current_car()["model"]

    def __get_random_car_by_pattern(self, car_data, pattern=""):

        if not pattern:
            pattern = "{brand} {model}"

        result = str(pattern)
        for key in self.get_keys():
            result = result.replace(f"{{{key}}}", str(car_data[key]))
        return result

    def __generate_random_car_vin(self):

        letters = string.ascii_uppercase
        digits = string.digits
        wmi = ''.join(choice(letters) for _ in range(3))
        vds = ''.join(choice(letters + digits) for _ in range(6))
        check_digit = choice(digits)
        vis = ''.join(choice(letters + digits) for _ in range(8))
        return wmi + vds + check_digit + vis
