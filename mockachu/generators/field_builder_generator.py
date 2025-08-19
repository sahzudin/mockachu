from .generator import Generator, GeneratorActionParameters, GeneratorActions
import re

class FieldBuilderGenerator(Generator):
    """Generator for building composite fields from other field data.
    
    Provides functionality to join and combine data from multiple fields
    using pattern-based templates. Allows creation of complex composite
    fields like full names, addresses, or formatted identifiers.
    """
    
    def __init__(self):
        """Initialize the FieldBuilderGenerator.
        
        No initialization parameters required for field building operations.
        """
        pass

    def get_actions(self):
        """Get the list of supported generator actions.
        
        Returns:
            list: List containing GeneratorActions.FIELD_JOIN
        """
        return [
            GeneratorActions.FIELD_JOIN
        ]

    def get_parameters(self, action):
        """Get the parameters required for a specific action.
        
        Args:
            action (GeneratorActions): The action to get parameters for
            
        Returns:
            list: List containing PATTERN parameter for field joining
        """
        match action:
            case GeneratorActions.FIELD_JOIN:
                return [GeneratorActionParameters.PATTERN.name]
        return []

    def get_keys(self):
        """Get the data keys that this generator can produce.
        
        Returns:
            list: List of data keys from parent class
        """
        return super().get_keys()

    def generate(self, action, *args):
        """Generate composite field data based on the specified action.
        
        Args:
            action (GeneratorActions): The type of field building to perform
            *args: Pattern and field data for joining
            
        Returns:
            str: Composite field value based on pattern and input data
        """
        match action:
            case GeneratorActions.FIELD_JOIN:
                return self.__generate_field_join(*args)
        return ""

    def get_pattern_example(self, action):
        """Get example patterns for field building actions.
        
        Args:
            action (GeneratorActions): The action to get pattern example for
            
        Returns:
            str: Example pattern string for the specified action
        """
        match action:
            case GeneratorActions.FIELD_JOIN:
                return "{field_1}.{field_2}+{field_3}"
        return super().get_pattern_example(action)

    def __generate_field_join(self, pattern="", **field_values):
        """
        Generate a joined field using a pattern with field placeholders

        Args:
            pattern: Pattern string with field placeholders like "{field1}.{field2}@test.com"
            **field_values: Dictionary of field values from the current row

        Returns:
            String with placeholders replaced by actual field values
        """
        if not pattern:
            return ""

        if field_values and isinstance(field_values, dict):
            pass
        else:
            return pattern

        result = pattern

        field_pattern = r'\{([^}:]+)(?::([^}]*))?\}'
        matches = re.findall(field_pattern, result)

        for field_name, format_spec in matches:
            field_value = field_values.get(field_name)

            if field_value is not None:
                field_value_str = str(field_value)

                if format_spec:
                    try:
                        if format_spec.startswith('0') and format_spec.endswith('d'):
                            padding = int(format_spec[:-1])
                            if field_value_str.isdigit():
                                field_value_str = field_value_str.zfill(
                                    padding)
                    except:
                        pass
            else:
                field_value_str = f"{{missing:{field_name}}}"

            if format_spec:
                placeholder = f"{{{field_name}:{format_spec}}}"
            else:
                placeholder = f"{{{field_name}}}"
            result = result.replace(placeholder, field_value_str)

        return result

    def set_current_row_data(self, row_data):
        """
        Set the current row data for field joining
        This method will be called by the data generator before generating values
        """
        self.current_row_data = row_data

    def generate_with_context(self, action, row_data, *args):
        """
        Generate a value with access to the current row's data
        This is used specifically for field joining
        """
        match action:
            case GeneratorActions.FIELD_JOIN:
                pattern = args[0] if args else ""
                return self.__generate_field_join(pattern, **row_data)
        return ""
