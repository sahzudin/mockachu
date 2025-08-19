from .generator import Generator, GeneratorActions
from random import choice

class YesNoGenerator(Generator):
    """Generator for boolean and yes/no related mock data.
    
    Provides generation of various boolean representations including
    true/false, 1/0 bits, yes/no strings, and y/n abbreviations.
    """
    
    def get_actions(self):
        """Get the list of supported generator actions.
        
        Returns:
            list: List of GeneratorActions for boolean data generation
        """
        return [
            GeneratorActions.RANDOM_BOOLEAN,
            GeneratorActions.RANDOM_BIT,
            GeneratorActions.RANDOM_YES_NO,
            GeneratorActions.RANDOM_Y_N
        ]

    def get_parameters(self, action):
        """Get the parameters required for a specific action.
        
        Args:
            action (GeneratorActions): The action to get parameters for
            
        Returns:
            list: Empty list as boolean actions don't require parameters
        """
        return []

    def get_keys(self):
        """Get the data keys that this generator can produce.
        
        Returns:
            list: List of data keys from parent class
        """
        return super().get_keys()

    def generate(self, action, *args):
        """Generate boolean data based on the specified action.
        
        Args:
            action (GeneratorActions): The type of boolean data to generate
            *args: Additional arguments (not used by boolean generator)
            
        Returns:
            bool, int, or str: Generated boolean data in the requested format
        """
        match action:
            case GeneratorActions.RANDOM_BOOLEAN:
                return self.__generate_random_boolean()
            case GeneratorActions.RANDOM_BIT:
                return self.__generate_random_bit()
            case GeneratorActions.RANDOM_YES_NO:
                return self.__generate_random_yes_no()
            case GeneratorActions.RANDOM_Y_N:
                return self.__generate_random_y_n()

    def __generate_random_boolean(self):
        """Generate a random boolean value as string.
        
        Returns:
            str: Random "true" or "false" string
        """
        return choice(["true", "false"])

    def __generate_random_bit(self):
        """Generate a random bit value.
        
        Returns:
            int: Random 0 or 1 integer
        """
        return choice([0, 1])

    def __generate_random_yes_no(self):
        """Generate a random yes/no value.
        
        Returns:
            str: Random "yes" or "no" string
        """
        return choice(["yes", "no"])

    def __generate_random_y_n(self):
        """Generate a random y/n abbreviation.
        
        Returns:
            str: Random "y" or "n" string
        """
        return choice(["y", "n"])
