import random
from ..generators.generator import GeneratorActions, GeneratorFormats, Generators
from ..generators.generator_identifier import GeneratorIdentifier
from multiprocessing import cpu_count
import concurrent.futures
import numpy as np

class DataGenerator:
    """Service for generating mock data based on field configurations.
    
    Handles the coordination of multiple generators to produce mock datasets
    with specified rows and formats. Supports multi-threaded generation for
    performance and manages generator state and configuration.
    """
    
    __generator_identifier = None

    def __init__(self) -> None:
        """Initialize the DataGenerator with generator identification service.
        
        Sets up the generator identifier for managing available generators.
        """
        self.__generator_identifier = GeneratorIdentifier()

    def reset_generators(self):
        """Reset all temporary generator states.
        
        Clears any temporary state in generators, useful for ensuring
        clean generation between different datasets.
        """
        self.__generator_identifier.reset_temporary_generators()

    def generate(self, request):
        """Generate mock data based on the provided request configuration.
        
        Args:
            request (dict): Configuration containing fields, rows, and format specifications
            
        Returns:
            Generated data in the requested format
        """
        fields = request["fields"]
        rows = request["rows"]

        request["format"] = GeneratorFormats[request["format"]]

        for field in fields:
            field["generator"] = Generators[field["generator"]]
            field["action"] = GeneratorActions[field["action"]]

        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = []
            chunk_size = int(rows / cpu_count())
            if chunk_size == 0:
                chunk_size = 1
            for i in range(0, rows, chunk_size):
                futures.append(executor.submit(list, self.__generate_data_cells(
                    i, min(i + chunk_size, rows), fields)))

            data_out = np.array([])
            for future in concurrent.futures.as_completed(futures):
                data_out = np.concatenate((data_out, future.result()))
            data_list = data_out.tolist()
            self.__initialize_sequence_fields(fields, data_list)
            self.__initialize_custom_list_sequence_fields(fields, data_list)
            return data_list

    def __initialize_sequence_fields(self, fields, data_list):
        sequence_fields = [
            field for field in fields if field["generator"].name == "SEQUENCE_GENERATOR"]
        for index, item in enumerate(data_list):
            for field in sequence_fields:
                start_sequence = 1
                interval = 1

                parameters = field.get("parameters")
                if parameters is not None and len(parameters) > 0:
                    if parameters[0] is not None:
                        try:
                            start_sequence = int(parameters[0])
                        except (ValueError, TypeError):
                            start_sequence = 1

                    if len(parameters) > 1 and parameters[1] is not None:
                        try:
                            interval = int(parameters[1])
                            interval = max(-1000, min(1000, interval)
                                           ) if interval != 0 else 1
                        except (ValueError, TypeError):
                            interval = 1

                item[field["name"]] = start_sequence + (index * interval)

    def __initialize_custom_list_sequence_fields(self, fields, data_list):

        from ..generators.custom_list_generator import CustomListGenerator

        sequential_custom_list_fields = [
            field for field in fields
            if field["generator"].name == "CUSTOM_LIST_GENERATOR"
            and field["action"].name == "SEQUENTIAL_CUSTOM_LIST_ITEM"
        ]

        for field in sequential_custom_list_fields:
            custom_list = ""
            parameters = field.get("parameters")
            if parameters and len(parameters) > 0:
                custom_list = parameters[0]

            if not custom_list:
                continue

            temp_generator = CustomListGenerator()
            items = temp_generator._CustomListGenerator__parse_custom_list(
                custom_list)

            if not items:
                continue

            for index, item in enumerate(data_list):
                item[field["name"]] = items[index % len(items)]

    def __generate_data_cells(self, start, end, fields):
        for _ in range(start, end):
            person_generators = []
            for field in fields:
                if field["generator"].name == "PERSON_GENERATOR":
                    generator = self.__generator_identifier.get_generator_by_identifier(
                        field["generator"])
                    if generator not in person_generators:
                        person_generators.append(generator)
                        generator.start_new_row()

            car_generators = []
            for field in fields:
                if field["generator"].name == "CAR_GENERATOR":
                    generator = self.__generator_identifier.get_generator_by_identifier(
                        field["generator"])
                    if generator not in car_generators:
                        car_generators.append(generator)
                        generator.start_new_row()

            geo_generators = []
            for field in fields:
                if field["generator"].name == "GEO_GENERATOR":
                    generator = self.__generator_identifier.get_generator_by_identifier(
                        field["generator"])
                    if generator not in geo_generators:
                        geo_generators.append(generator)
                        generator.start_new_row()

            data_cell = {}

            field_join_generators = []
            regular_fields = []

            for field in fields:
                if field["generator"].name == "FIELD_BUILDER_GENERATOR":
                    field_join_generators.append(field)
                else:
                    regular_fields.append(field)

            for field in regular_fields:
                generator = self.__generator_identifier.get_generator_by_identifier(
                    field["generator"])
                if (field["nullable_percentage"] == 0):
                    if "parameters" in field and field["parameters"]:
                        data_cell[field["name"]] = generator.generate(
                            field["action"], *field["parameters"])
                    else:
                        data_cell[field["name"]] = generator.generate(
                            field["action"])
                elif (field["nullable_percentage"] == 100):
                    data_cell[field["name"]] = None
                else:
                    random_number = random.randint(1, 100)
                    if (random_number <= field["nullable_percentage"]):
                        data_cell[field["name"]] = None
                    else:
                        if "parameters" in field and field["parameters"]:
                            data_cell[field["name"]] = generator.generate(
                                field["action"], *field["parameters"])
                        else:
                            data_cell[field["name"]] = generator.generate(
                                field["action"])

            for field in field_join_generators:
                generator = self.__generator_identifier.get_generator_by_identifier(
                    field["generator"])

                if (field["nullable_percentage"] == 0):
                    if "parameters" in field and field["parameters"]:
                        data_cell[field["name"]] = generator.generate_with_context(
                            field["action"], data_cell, *field["parameters"])
                    else:
                        data_cell[field["name"]] = generator.generate_with_context(
                            field["action"], data_cell)
                elif (field["nullable_percentage"] == 100):
                    data_cell[field["name"]] = None
                else:
                    random_number = random.randint(1, 100)
                    if (random_number <= field["nullable_percentage"]):
                        data_cell[field["name"]] = None
                    else:
                        if "parameters" in field and field["parameters"]:
                            data_cell[field["name"]] = generator.generate_with_context(
                                field["action"], data_cell, *field["parameters"])
                        else:
                            data_cell[field["name"]] = generator.generate_with_context(
                                field["action"], data_cell)

            yield data_cell
