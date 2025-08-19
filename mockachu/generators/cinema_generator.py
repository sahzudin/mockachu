from .generator import Generator, GeneratorActions
from random import choice
from ..services.file_reader import read_resource_file_lines

class CinemaGenerator(Generator):
    """Generator for cinema and entertainment-related mock data.
    
    Provides generation of movie titles and TV series names from predefined
    lists of popular entertainment content. Useful for creating realistic
    entertainment-related datasets.
    """
    
    def get_actions(self):
        """Get the list of supported generator actions.
        
        Returns:
            list: List of GeneratorActions for cinema data generation
        """
        return [GeneratorActions.RANDOM_MOVIE, GeneratorActions.RANDOM_SERIE]

    def get_parameters(self, action):
        """Get the parameters required for a specific action.
        
        Args:
            action (GeneratorActions): The action to get parameters for
            
        Returns:
            list: Empty list as cinema actions don't require parameters
        """
        return []

    def get_keys(self):
        """Get the data keys that this generator can produce.
        
        Returns:
            list: List of data keys from parent class
        """
        return super().get_keys()

    def generate(self, action, *args):
        """Generate cinema data based on the specified action.
        
        Args:
            action (GeneratorActions): The type of cinema data to generate
            *args: Additional arguments (not used by cinema generator)
            
        Returns:
            str: Generated movie title or TV series name
        """
        match action:
            case GeneratorActions.RANDOM_MOVIE:
                return self.__generate_random_movie()
            case GeneratorActions.RANDOM_SERIE:
                return self.__generate_random_serie()

    def __generate_random_movie(self):
        """Generate a random movie title.
        
        Returns:
            str: Random movie title from the loaded movies list
        """
        movies = read_resource_file_lines("movies.txt")
        return choice(movies)

    def __generate_random_serie(self):
        """Generate a random TV series name.
        
        Returns:
            str: Random TV series name from the loaded series list
        """
        series = read_resource_file_lines("series.txt")
        return choice(series)
