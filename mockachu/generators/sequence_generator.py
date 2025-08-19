from .generator import Generator, GeneratorActionParameters, GeneratorActions

class SequenceGenerator(Generator):
    """Generator for sequential numeric data.
    
    Provides generation of sequential numbers with configurable starting values
    and intervals. Supports both positive and negative intervals for ascending
    or descending sequences. Maintains state to generate continuous sequences.
    """
    
    __start_sequence = 0
    __interval = 1

    def __init__(self, start_sequence=1, interval=1) -> None:
        """Initialize the SequenceGenerator with starting value and interval.
        
        Args:
            start_sequence (int): Starting value for the sequence (default: 1)
            interval (int): Increment between sequential values (default: 1)
        """
        self.__start_sequence = start_sequence
        self.__interval = max(-1000, min(1000, interval)
                              ) if interval != 0 else 1

    def get_actions(self):
        """Get the list of supported generator actions.
        
        Returns:
            list: List containing GeneratorActions.SEQUENTIAL_NUMBER
        """
        return [GeneratorActions.SEQUENTIAL_NUMBER]

    def get_parameters(self, action):
        """Get the parameters required for a specific action.
        
        Args:
            action (GeneratorActions): The action to get parameters for
            
        Returns:
            list: List of required parameters for sequential number generation
        """
        match action:
            case GeneratorActions.SEQUENTIAL_NUMBER:
                return [GeneratorActionParameters.START_SEQUENCE.name, GeneratorActionParameters.INTERVAL_SEQUENCE.name]
        return []

    def get_keys(self):
        """Get the data keys that this generator can produce.
        
        Returns:
            list: List of data keys from parent class
        """
        return super().get_keys()

    def generate(self, action, *args):
        """Generate sequential numbers with configurable start and interval

        Args:
            action: The generator action (SEQUENTIAL_NUMBER)
            *args: Parameters - start_sequence and interval_sequence

        Returns:
            int: The configured starting number (actual sequence handled by data generator)
        """
        match action:
            case GeneratorActions.SEQUENTIAL_NUMBER:
                if args and len(args) >= 1:
                    try:
                        start = int(args[0])
                        self.__start_sequence = start
                    except (ValueError, TypeError):
                        self.__start_sequence = 1

                if args and len(args) >= 2:
                    try:
                        interval = int(args[1])
                        interval = max(-1000, min(1000, interval)
                                       ) if interval != 0 else 1
                        self.__interval = interval
                    except (ValueError, TypeError):
                        self.__interval = 1

                return self.__start_sequence

        return 0  # fallback

    def get_next_value(self):
        """Get the next value in the sequence and advance the counter.
        
        Returns:
            int: The next sequential value based on current position and interval
        """
        current_value = self.__start_sequence
        self.__start_sequence += self.__interval
        return current_value

    def reset_sequence(self, start_value=1, interval=1):
        """Reset the sequence to new starting values.
        
        Args:
            start_value (int): New starting value for the sequence (default: 1)
            interval (int): New increment between values (default: 1)
        """
        self.__start_sequence = start_value
        self.__interval = max(-1000, min(1000, interval)
                              ) if interval != 0 else 1
