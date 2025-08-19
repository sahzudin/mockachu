from .generator import Generator, GeneratorActions
from random import choice
from ..services.file_reader import read_resource_file_lines

class BiologyGenerator(Generator):
    """Generator for biology-related mock data.
    
    Provides random generation of animals and plants from predefined lists.
    Used for creating realistic biology-related data in mock datasets.
    """
    
    def get_actions(self):
        """Get the list of supported generator actions.
        
        Returns:
            list: List of GeneratorActions supported by this generator
        """
        return [GeneratorActions.RANDOM_ANIMAL, GeneratorActions.RANDOM_PLANT]

    def get_parameters(self, action):
        """Get the parameters required for a specific action.
        
        Args:
            action (GeneratorActions): The action to get parameters for
            
        Returns:
            list: Empty list as biology actions don't require parameters
        """
        return []

    def get_keys(self):
        """Get the data keys that this generator can produce.
        
        Returns:
            list: List of data keys from parent class
        """
        return super().get_keys()

    def generate(self, action, *args):
        """Generate biology-related data based on the specified action.
        
        Args:
            action (GeneratorActions): The type of biology data to generate
            *args: Additional arguments (not used by biology generator)
            
        Returns:
            str: Generated biology data (animal or plant name)
        """
        match action:
            case GeneratorActions.RANDOM_ANIMAL:
                return self.__generate_random_animal()
            case GeneratorActions.RANDOM_PLANT:
                return self.__generate_random_plant()

    __animals = []
    __plants = []

    def __init__(self) -> None:
        """Initialize the BiologyGenerator with animal and plant data.
        
        Loads animal and plant names from resource files for random selection.
        """
        self.__animals = read_resource_file_lines("animals.txt")
        self.__plants = read_resource_file_lines("plants.txt")

    def __generate_random_animal(self):
        """Generate a random animal name.
        
        Returns:
            str: Random animal name from the loaded animal list
        """
        return choice(self.__animals)

    def __generate_random_plant(self):
        """Generate a random plant name.
        
        Returns:
            str: Random plant name from the loaded plant list
        """
        return choice(self.__plants)
