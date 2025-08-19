from .generator import Generator, GeneratorActionParameters, GeneratorActions
from random import choice
from ..services.file_reader import read_resource_file_json

class ColorGenerator(Generator):
    """Generator for color-related mock data.
    
    Provides random generation of colors in various formats including common colors,
    HTML colors, hex codes, and pattern-based color generation. Supports both
    common color names and comprehensive HTML color specifications.
    """
    
    def get_actions(self):
        """Get the list of supported generator actions.
        
        Returns:
            list: List of GeneratorActions for color generation
        """
        return [
            GeneratorActions.RANDOM_COMMON_COLOR,
            GeneratorActions.RANDOM_COMMON_COLOR_HEX,
            GeneratorActions.RANDOM_COMMON_COLOR_WITH_HEX,
            GeneratorActions.RANDOM_COMMON_COLOR_PATTERN,
            GeneratorActions.RANDOM_HTML_COLOR,
            GeneratorActions.RANDOM_HTML_COLOR_HEX,
            GeneratorActions.RANDOM_HTML_COLOR_WITH_HEX,
            GeneratorActions.RANDOM_HTML_COLOR_PATTERN
        ]

    def get_parameters(self, action):
        """Get the parameters required for a specific action.
        
        Args:
            action (GeneratorActions): The action to get parameters for
            
        Returns:
            list: List of required parameters for pattern-based actions
        """
        match action:
            case GeneratorActions.RANDOM_COMMON_COLOR_PATTERN | GeneratorActions.RANDOM_HTML_COLOR_PATTERN:
                return [GeneratorActionParameters.PATTERN.name]
        return []

    def get_keys(self):
        """Get the data keys that this generator can produce.
        
        Returns:
            list: List of data keys including 'name' and 'hex'
        """
        return ["name", "hex"]

    def get_pattern_example(self, action):
        """Get example patterns for pattern-based color generation.
        
        Args:
            action (GeneratorActions): The action to get pattern example for
            
        Returns:
            str: Example pattern string for the specified action
        """
        match action:
            case GeneratorActions.RANDOM_COMMON_COLOR_PATTERN:
                return "{name} ({hex})"
            case GeneratorActions.RANDOM_HTML_COLOR_PATTERN:
                return "{name} - {hex}"
        return super().get_pattern_example(action)

    def generate(self, action, *args):
        """Generate color data based on the specified action.
        
        Args:
            action (GeneratorActions): The type of color data to generate
            *args: Additional arguments (pattern for pattern-based actions)
            
        Returns:
            str or dict: Generated color data in the requested format
        """
        match action:
            case GeneratorActions.RANDOM_COMMON_COLOR:
                return self.__get_random_common_color()
            case GeneratorActions.RANDOM_COMMON_COLOR_HEX:
                return self.__get_random_common_color_hex()
            case GeneratorActions.RANDOM_COMMON_COLOR_WITH_HEX:
                return self.__get_random_common_color_with_hex()
            case GeneratorActions.RANDOM_COMMON_COLOR_PATTERN:
                return self.__get_random_common_color_by_pattern() if super().args_empty(args) else self.__get_random_common_color_by_pattern(args[0])
            case GeneratorActions.RANDOM_HTML_COLOR:
                return self.__get_random_html_color()
            case GeneratorActions.RANDOM_HTML_COLOR_HEX:
                return self.__get_random_html_color_hex()
            case GeneratorActions.RANDOM_HTML_COLOR_WITH_HEX:
                return self.__get_random_html_color_with_hex()
            case GeneratorActions.RANDOM_HTML_COLOR_PATTERN:
                return self.__get_random_html_color_by_pattern() if super().args_empty(args) else self.__get_random_html_color_by_pattern(args[0])

    __common_colors = []
    __html_colors = []

    def __init__(self) -> None:
        """Initialize the ColorGenerator with color data.
        
        Loads common colors and HTML colors from resource files for random selection.
        """
        self.__common_colors = read_resource_file_json("common_colors.json")
        self.__html_colors = read_resource_file_json("html_colors.json")

    def __get_random_common_color(self):
        random_color = choice(self.__common_colors)
        return random_color["name"]

    def __get_random_common_color_hex(self):
        random_color = choice(self.__common_colors)
        return random_color["hex"]

    def __get_random_common_color_with_hex(self):
        random_color = choice(self.__common_colors)
        return random_color["name"] + ' - ' + random_color["hex"]

    def __get_random_common_color_by_pattern(self, pattern=""):
        random_color = choice(self.__common_colors)
        for key in self.get_keys():
            pattern = str(pattern).replace(
                f"{{{key}}}", str(random_color[key]))
        return pattern

    def __get_random_html_color(self):
        random_color = choice(self.__html_colors)
        return random_color["name"]

    def __get_random_html_color_hex(self):
        random_color = choice(self.__html_colors)
        return random_color["hex"]

    def __get_random_html_color_with_hex(self):
        random_color = choice(self.__html_colors)
        return random_color["name"] + ' - ' + random_color["hex"]

    def __get_random_html_color_by_pattern(self, pattern=""):
        random_color = choice(self.__html_colors)
        for key in self.get_keys():
            pattern = str(pattern).replace(
                f"{{{key}}}", str(random_color[key]))
        return pattern
