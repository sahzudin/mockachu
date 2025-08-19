from .generator import Generator, GeneratorActionParameters, GeneratorActions
from random import choice
import pytz
import csv
import os


class GeoGenerator(Generator):
    """Generator for geographic and location-related mock data.
    
    Provides generation of geographic data including cities, countries, timezones,
    country codes, and location-based information. Maintains consistency within
    a row for related geographic attributes to ensure realistic combinations.
    """
    
    def __init__(self) -> None:
        """Initialize the GeoGenerator with world cities data.
        
        Loads world cities data from CSV file and initializes row-based
        location tracking for geographic consistency.
        """
        current_dir = os.path.dirname(os.path.dirname(__file__))
        cities_file = os.path.join(current_dir, "res", "world_cities.csv")

        self.__geo_data = []
        with open(cities_file, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.__geo_data.append(row)

        self._current_row_location = None  # Location data for current row
        self._row_initialized = False  # Flag to track if current row location is set

    def get_actions(self):
        """Get the list of supported generator actions.
        
        Returns:
            list: List of GeneratorActions for geographic data generation
        """
        return [
            GeneratorActions.RANDOM_TIMEZONE,
            # GeneratorActions.RANDOM_GEO_DATA, #skipped into mvp version
            GeneratorActions.RANDOM_CITY,
            GeneratorActions.RANDOM_COUNTRY,
            GeneratorActions.RANDOM_CITY_BY_COUNTRY,
            GeneratorActions.RANDOM_COUNTRY_ISO_CODE_2,
            GeneratorActions.RANDOM_COUNTRY_ISO_CODE_3,
            GeneratorActions.RANDOM_GEO_DATA_PATTERN
        ]

    def get_parameters(self, action):
        match action:
            case GeneratorActions.RANDOM_CITY_BY_COUNTRY:
                return [GeneratorActionParameters.COUNTRIES_LIST.name]
            case GeneratorActions.RANDOM_GEO_DATA_PATTERN:
                return [GeneratorActionParameters.PATTERN.name]
        return []

    def get_keys(self):
        return ["city", "country", "iso_code_2", "iso_code_3"]

    def get_available_countries(self):
        countries = set()
        for location in self.__geo_data:
            countries.add(location["country"])
        return sorted(list(countries))

    def get_pattern_example(self, action):
        match action:
            case GeneratorActions.RANDOM_GEO_DATA_PATTERN:
                return "{city}, {country} ({iso_code_2})"
        return super().get_pattern_example(action)

    def _generate_location_data(self):
        random_location = choice(self.__geo_data)

        return {
            "city": random_location["city"],
            "country": random_location["country"],
            "iso_code_2": random_location["iso_code_2"],
            "iso_code_3": random_location["iso_code_3"]
        }

    def _get_current_location(self):
        if not self._row_initialized:
            self._current_row_location = self._generate_location_data()
            self._row_initialized = True
        return self._current_row_location

    def start_new_row(self):
        """Start a new row by resetting location state.
        
        Clears the current row location data to ensure fresh geographic
        data selection for the next row generation.
        """
        self._row_initialized = False
        self._current_row_location = None

    def generate(self, action, *args):
        """Generate geographic data based on the specified action.
        
        Args:
            action (GeneratorActions): The type of geographic data to generate
            *args: Additional arguments (countries list for filtered selection)
            
        Returns:
            str or dict: Generated geographic data (city, country, timezone, etc.)
        """
        if action == GeneratorActions.RANDOM_TIMEZONE:
            return self.__get_random_timezone()

        location_data = self._get_current_location()

        match action:
            case GeneratorActions.RANDOM_GEO_DATA:
                return location_data
            case GeneratorActions.RANDOM_CITY:
                return location_data["city"]
            case GeneratorActions.RANDOM_COUNTRY:
                return location_data["country"]
            case GeneratorActions.RANDOM_COUNTRY_ISO_CODE_2:
                return location_data["iso_code_2"]
            case GeneratorActions.RANDOM_COUNTRY_ISO_CODE_3:
                return location_data["iso_code_3"]
            case GeneratorActions.RANDOM_CITY_BY_COUNTRY:
                if not super().args_empty(args):
                    return self.__get_random_city_by_countries(args[0])
                return location_data["city"]
            case GeneratorActions.RANDOM_GEO_DATA_PATTERN:
                return self.__get_random_geo_data_by_pattern(location_data) if super().args_empty(args) else self.__get_random_geo_data_by_pattern(location_data, args[0])

    def __get_random_timezone(self):
        return choice(pytz.all_timezones)

    def __get_random_city_by_countries(self, countries_string):
        if not countries_string:
            return self._get_current_location()["city"]

        if isinstance(countries_string, str):
            selected_countries = [country.strip()
                                  for country in countries_string.split(',')]
        else:
            selected_countries = countries_string

        cities = []
        for item in self.__geo_data:
            if item["country"] in selected_countries:
                cities.append(item["city"])

        return choice(cities) if cities else self._get_current_location()["city"]

    def __get_random_geo_data_by_pattern(self, location_data, pattern=""):
        if not pattern:
            pattern = "{city}, {country} ({iso_code_2})"

        result = str(pattern)
        for key in self.get_keys():
            result = result.replace(f"{{{key}}}", str(location_data[key]))
        return result
