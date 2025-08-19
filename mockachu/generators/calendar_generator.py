from .generator import Generator, GeneratorActionParameters, GeneratorActions
from datetime import datetime, time, timedelta
from random import randint


class CalendarGenerator(Generator):
    """Generator for calendar and datetime-related mock data.
    
    Provides generation of dates, times, datetimes, and Unix timestamps
    with configurable ranges and formats. Supports various datetime formats
    and validation of date/time ranges.
    """
    
    def get_actions(self):
        """Get the list of supported generator actions.
        
        Returns:
            list: List of GeneratorActions for calendar data generation
        """
        return [
            GeneratorActions.RANDOM_DATE,
            GeneratorActions.RANDOM_TIME,
            GeneratorActions.RANDOM_DATE_TIME,
            GeneratorActions.RANDOM_UNIX_TIMESTAMP
        ]

    def get_parameters(self, action):
        """Get the parameters required for a specific action.
        
        Args:
            action (GeneratorActions): The action to get parameters for
            
        Returns:
            list: List of required parameters for datetime generation
        """
        match action:
            case GeneratorActions.RANDOM_DATE:
                return [GeneratorActionParameters.START_DATE.name, GeneratorActionParameters.END_DATE.name,
                        GeneratorActionParameters.DATE_FORMAT.name]
            case GeneratorActions.RANDOM_TIME:
                return [GeneratorActionParameters.START_TIME.name, GeneratorActionParameters.END_TIME.name,
                        GeneratorActionParameters.TIME_FORMAT.name]
            case GeneratorActions.RANDOM_DATE_TIME:
                return [GeneratorActionParameters.START_DATE.name, GeneratorActionParameters.END_DATE.name,
                        GeneratorActionParameters.START_TIME.name, GeneratorActionParameters.END_TIME.name,
                        GeneratorActionParameters.DATETIME_FORMAT.name]
            case GeneratorActions.RANDOM_UNIX_TIMESTAMP:
                return [GeneratorActionParameters.START_TIMESTAMP.name, GeneratorActionParameters.END_TIMESTAMP.name]
        return []

    def get_keys(self):
        """Get the data keys that this generator can produce.
        
        Returns:
            list: List of data keys from parent class
        """
        return super().get_keys()

    def generate(self, action, *args):
        """Generate calendar data based on the specified action.
        
        Args:
            action (GeneratorActions): The type of calendar data to generate
            *args: Parameters for date/time generation (start, end, format)
            
        Returns:
            str or int: Generated date, time, datetime, or timestamp value
        """
        match action:
            case GeneratorActions.RANDOM_DATE:
                if super().args_empty(args):
                    return self.generate_random_date()
                else:
                    start_date = self._parse_date_parameter(
                        args[0]) if len(args) > 0 else None
                    end_date = self._parse_date_parameter(
                        args[1]) if len(args) > 1 else None
                    date_format = args[2] if len(
                        args) > 2 and args[2] else None
                    return self.generate_random_date(start_date, end_date, date_format)
            case GeneratorActions.RANDOM_TIME:
                if super().args_empty(args):
                    return self.generate_random_time()
                else:
                    start_time = self._parse_time_parameter(
                        args[0]) if len(args) > 0 else None
                    end_time = self._parse_time_parameter(
                        args[1]) if len(args) > 1 else None
                    time_format = args[2] if len(
                        args) > 2 and args[2] else None
                    return self.generate_random_time(start_time, end_time, time_format)
            case GeneratorActions.RANDOM_DATE_TIME:
                if super().args_empty(args):
                    return self.generate_random_date_time()
                else:
                    start_date = self._parse_date_parameter(
                        args[0]) if len(args) > 0 else None
                    end_date = self._parse_date_parameter(
                        args[1]) if len(args) > 1 else None
                    start_time = self._parse_time_parameter(
                        args[2]) if len(args) > 2 else None
                    end_time = self._parse_time_parameter(
                        args[3]) if len(args) > 3 else None
                    datetime_format = args[4] if len(
                        args) > 4 and args[4] else None
                    return self.generate_random_date_time(start_date, end_date, start_time, end_time, datetime_format=datetime_format)
            case GeneratorActions.RANDOM_UNIX_TIMESTAMP:
                if super().args_empty(args):
                    return self.generate_random_unix_timestamp()
                else:
                    start_timestamp = args[0] if len(args) > 0 else None
                    end_timestamp = args[1] if len(args) > 1 else None
                    return self.generate_random_unix_timestamp(start_timestamp, end_timestamp)

    __date_format = "%Y-%m-%d"
    __time_format = "%H:%M:%S"

    def __init__(self, date_format=None, time_format=None) -> None:
        if (date_format is not None):
            self.__date_format = date_format
        if (time_format is not None):
            self.__time_format = time_format

    def _parse_date_parameter(self, date_param):
        if date_param is None or date_param == "":
            return None

        if isinstance(date_param, datetime):
            return date_param

        if isinstance(date_param, str):
            try:
                return datetime.strptime(date_param, "%Y-%m-%d")
            except ValueError:
                try:
                    return datetime.strptime(date_param, "%Y/%m/%d")
                except ValueError:
                    print(
                        f"Warning: Could not parse date '{date_param}', using default")
                    return None
        return None

    def _parse_time_parameter(self, time_param):
        if time_param is None or time_param == "":
            return None

        if isinstance(time_param, time):
            return time_param

        if isinstance(time_param, str):
            try:
                time_obj = datetime.strptime(time_param, "%H:%M:%S").time()
                return time_obj
            except ValueError:
                try:
                    time_obj = datetime.strptime(time_param, "%H:%M").time()
                    return time_obj
                except ValueError:
                    print(
                        f"Warning: Could not parse time '{time_param}', using default")
                    return None
        return None

    def generate_random_date(self, start_date=None, end_date=None, date_format=None):
        if start_date is None:
            start_date = datetime(1970, 1, 1)
        if end_date is None:
            end_date = datetime.now()

        delta = end_date - start_date
        random_days = randint(0, delta.days)
        random_date = start_date + timedelta(days=random_days)

        format_to_use = date_format if date_format else self.__date_format
        return random_date.strftime(format_to_use)

    def generate_random_time(self, start_time=None, end_time=None, time_format=None):
        if start_time is None:
            start_time = time(0, 0)
        if end_time is None:
            end_time = time(23, 59)

        from_seconds = start_time.hour * 3600 + \
            start_time.minute * 60 + start_time.second
        to_seconds = end_time.hour * 3600 + end_time.minute * 60 + end_time.second

        random_seconds = randint(from_seconds, to_seconds)
        random_time = time(random_seconds // 3600,
                           (random_seconds % 3600) // 60, random_seconds % 60)

        format_to_use = time_format if time_format else self.__time_format
        return random_time.strftime(format_to_use)

    def generate_random_date_time(self, start_date=None, end_date=None, start_time=None, end_time=None, date_format=None, time_format=None, datetime_format=None):
        if datetime_format:
            if start_date is None:
                start_date = datetime(1970, 1, 1)
            if end_date is None:
                end_date = datetime.now()
            if start_time is None:
                start_time = time(0, 0)
            if end_time is None:
                end_time = time(23, 59)

            start_datetime = datetime.combine(start_date.date() if hasattr(
                start_date, 'date') else start_date, start_time)
            end_datetime = datetime.combine(end_date.date() if hasattr(
                end_date, 'date') else end_date, end_time)

            delta = end_datetime - start_datetime
            if delta.total_seconds() <= 0:
                random_datetime = start_datetime
            else:
                random_seconds = randint(0, int(delta.total_seconds()))
                random_datetime = start_datetime + \
                    timedelta(seconds=random_seconds)

            return random_datetime.strftime(datetime_format)
        else:
            date_part = self.generate_random_date(
                start_date, end_date, date_format)
            time_part = self.generate_random_time(
                start_time, end_time, time_format)
            return f"{date_part} {time_part}"

    def generate_random_unix_timestamp(self, start_timestamp=None, end_timestamp=None):
        if start_timestamp is None:
            start_timestamp = 0
        if end_timestamp is None:
            end_timestamp = int(datetime.now().timestamp())

        random_unix_timestamp = randint(start_timestamp, end_timestamp)
        return random_unix_timestamp
