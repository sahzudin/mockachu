from .color_generator import ColorGenerator
from .calendar_generator import CalendarGenerator
from .biology_generator import BiologyGenerator
from .person_generator import PersonGenerator
from .sequence_generator import SequenceGenerator
from .string_generator import StringNumberGenerator
from .yes_no_generator import YesNoGenerator
from .money_generator import MoneyGenerator
from .cinema_generator import CinemaGenerator
from .file_generator import FileGenerator
from .car_generator import CarGenerator
from .geo_generator import GeoGenerator
from .it_generator import ItGenerator
from .custom_list_generator import CustomListGenerator
from .field_builder_generator import FieldBuilderGenerator
from .generator import Generators


class GeneratorIdentifier:
    """Service for identifying and managing generator instances.
    
    Provides a centralized registry of all available generators and manages
    their instantiation and lifecycle. Uses shared instances for performance
    and maintains temporary generators for specific use cases.
    """
    
    _shared_generators = None

    def __init__(self) -> None:
        """Initialize the GeneratorIdentifier with shared generator instances.
        
        Creates singleton instances of all available generators for efficient
        reuse across data generation operations.
        """
        if GeneratorIdentifier._shared_generators is None:
            GeneratorIdentifier._shared_generators = {
                Generators.BIOLOGY_GENERATOR: BiologyGenerator(),
                Generators.CAR_GENERATOR: CarGenerator(),
                Generators.COLOR_GENERATOR: ColorGenerator(),
                Generators.FILE_GENERATOR: FileGenerator(),
                Generators.GEO_GENERATOR: GeoGenerator(),
                Generators.IT_GENERATOR: ItGenerator(),
                Generators.MONEY_GENERATOR: MoneyGenerator(),
                Generators.CINEMA_GENERATOR: CinemaGenerator(),
                Generators.YES_NO_GENERATOR: YesNoGenerator(),
                Generators.STRING_GENERATOR: StringNumberGenerator(),
                Generators.PERSON_GENERATOR: PersonGenerator(),
                Generators.CALENDAR_GENERATOR: CalendarGenerator(),
                Generators.SEQUENCE_GENERATOR: SequenceGenerator(),
                Generators.CUSTOM_LIST_GENERATOR: CustomListGenerator(),
                Generators.FIELD_BUILDER_GENERATOR: FieldBuilderGenerator()
            }
        self.__generators = GeneratorIdentifier._shared_generators

    def get_generator_by_identifier(self, identifier):
        return self.__generators.get(identifier)

    def reset_temporary_generators(self):
        GeneratorIdentifier._shared_generators[Generators.SEQUENCE_GENERATOR] = SequenceGenerator(
        )
        GeneratorIdentifier._shared_generators[Generators.CUSTOM_LIST_GENERATOR].reset_sequential_indices(
        )
