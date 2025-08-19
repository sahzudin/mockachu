from .generator import Generator, GeneratorActionParameters, GeneratorActions
from random import choice


class CustomListGenerator(Generator):
    """Generator for custom list-based mock data.
    
    Provides generation from user-defined custom lists with support for both
    random selection and sequential iteration through list items. Maintains
    separate state for each field to support multiple custom lists.
    """
    
    def __init__(self):
        """Initialize the CustomListGenerator with empty list storage.
        
        Sets up storage for custom lists and sequential indices tracking
        to support multiple fields with different custom lists.
        """
        self.__custom_lists = {}  # Store custom lists per field
        self.__sequential_indices = {}  # Track indices for sequential access

    def get_actions(self):
        """Get the list of supported generator actions.
        
        Returns:
            list: List of GeneratorActions for custom list data generation
        """
        return [
            GeneratorActions.RANDOM_CUSTOM_LIST_ITEM,
            GeneratorActions.SEQUENTIAL_CUSTOM_LIST_ITEM
        ]

    def get_parameters(self, action):
        """Get the parameters required for a specific action.
        
        Args:
            action (GeneratorActions): The action to get parameters for
            
        Returns:
            list: List containing CUSTOM_LIST parameter for both actions
        """
        match action:
            case GeneratorActions.RANDOM_CUSTOM_LIST_ITEM:
                return [GeneratorActionParameters.CUSTOM_LIST.name]
            case GeneratorActions.SEQUENTIAL_CUSTOM_LIST_ITEM:
                return [GeneratorActionParameters.CUSTOM_LIST.name]
        return []

    def get_keys(self):
        """Get the data keys that this generator can produce.
        
        Returns:
            list: List of data keys from parent class
        """
        return super().get_keys()

    def generate(self, action, *args):
        """Generate data from custom lists based on the specified action.
        
        Args:
            action (GeneratorActions): The type of custom list selection to perform
            *args: Custom list data and field identifier
            
        Returns:
            str: Selected item from the custom list
        """
        match action:
            case GeneratorActions.RANDOM_CUSTOM_LIST_ITEM:
                return self.__generate_random_custom_list_item(*args)
            case GeneratorActions.SEQUENTIAL_CUSTOM_LIST_ITEM:
                return self.__generate_sequential_custom_list_item(*args)
        return ""

    def __generate_random_custom_list_item(self, custom_list=""):

        if not custom_list:
            return ""

        items = self.__parse_custom_list(custom_list)
        if not items:
            return ""

        return choice(items)

    def __generate_sequential_custom_list_item(self, custom_list=""):

        if not custom_list:
            return ""

        list_key = hash(custom_list)

        items = self.__parse_custom_list(custom_list)
        if not items:
            return ""

        if list_key not in self.__sequential_indices:
            self.__sequential_indices[list_key] = 0

        current_index = self.__sequential_indices[list_key]
        item = items[current_index]

        self.__sequential_indices[list_key] = (current_index + 1) % len(items)

        return item

    def __parse_custom_list(self, custom_list):
        """Parse custom list from various formats (comma, semicolon, newline separated)"""
        if not custom_list:
            return []

        # First split by newlines to handle multi-line input
        lines = [line.strip() for line in custom_list.split('\n')]
        lines = [line for line in lines if line]  # Remove empty lines

        items = []

        for line in lines:
            # Handle mixed separators by replacing semicolons with commas first
            if ';' in line:
                line = line.replace(';', ',')

            # Now split by comma
            if ',' in line:
                line_items = [item.strip() for item in line.split(',')]
            else:
                line_items = [line.strip()]

            items.extend([item for item in line_items if item])

        # Fallback: if no items were parsed (single line input), try direct parsing
        if not items:
            # Handle mixed separators by replacing semicolons with commas first
            normalized_list = custom_list.replace(';', ',')

            if ',' in normalized_list:
                items = [item.strip() for item in normalized_list.split(',')]
            else:
                items = [custom_list.strip()]

            items = [item for item in items if item]

        return items

    def reset_sequential_indices(self):

        self.__sequential_indices.clear()
