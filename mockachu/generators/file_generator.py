from .generator import Generator, GeneratorActions
from .string_generator import StringNumberGenerator
from random import choice
import mimetypes

from ..services.file_reader import read_resource_file_lines


class FileGenerator(Generator):
    """Generator for file-related mock data.
    
    Provides generation of file names, file extensions, and MIME types.
    Useful for creating realistic file system related data in mock datasets.
    """
    
    def get_actions(self):
        """Get the list of supported generator actions.
        
        Returns:
            list: List of GeneratorActions for file data generation
        """
        return [
            GeneratorActions.RANDOM_FILE_NAME,
            GeneratorActions.RANDOM_FILE_EXTENSION,
            GeneratorActions.RANDOM_MIME_TYPE
        ]

    def get_parameters(self, action):
        """Get the parameters required for a specific action.
        
        Args:
            action (GeneratorActions): The action to get parameters for
            
        Returns:
            list: Empty list as file actions don't require parameters
        """
        return []

    def get_keys(self):
        """Get the data keys that this generator can produce.
        
        Returns:
            list: List of data keys from parent class
        """
        return super().get_keys()

    def generate(self, action, *args):
        """Generate file-related data based on the specified action.
        
        Args:
            action (GeneratorActions): The type of file data to generate
            *args: Additional arguments (not used by file generator)
            
        Returns:
            str: Generated file name, extension, or MIME type
        """
        match action:
            case GeneratorActions.RANDOM_FILE_NAME:
                return self.__generate_random_file_name()
            case GeneratorActions.RANDOM_FILE_EXTENSION:
                return self.__generate_random_file_extension()
            case GeneratorActions.RANDOM_MIME_TYPE:
                return self.__generate_random_mime_type()

    __random_string_generator = None
    __common_mime_types = []
    __common_file_extensions = []

    def __init__(self) -> None:
        self.__random_string_generator = StringNumberGenerator()
        self.__common_mime_types = list(mimetypes.types_map.values())
        self.__common_file_extensions = read_resource_file_lines(
            "file_extensions.txt")

    def __generate_random_file_name(self):
        file_name = self.__random_string_generator.generate(
            GeneratorActions.RANDOM_ALPHABETICAL_UPPERCASE_LOWERCASE_STRING, 10) + choice(self.__common_file_extensions)
        return file_name

    def __generate_random_file_extension(self):
        return choice(self.__common_file_extensions)

    def __generate_random_mime_type(self):
        return choice(self.__common_mime_types)
