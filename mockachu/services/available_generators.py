from ..generators.generator import GeneratorFormats, Generators
from ..generators.generator_identifier import GeneratorIdentifier

def get_available_generators():
    response = {
        "formats": [],
        "generators": []
    }

    formats_list = [format for format in GeneratorFormats]
    for format in formats_list:
        response["formats"].append(format.name)

    generator_identifier = GeneratorIdentifier()
    generators_list = [member for member in Generators]

    for generator_name in generators_list:
        generator = generator_identifier.get_generator_by_identifier(
            generator_name)

        generator_actions = generator.get_actions()
        actions = []

        for generator_action in generator_actions:
            display_name = generator.get_action_display_name(generator_action)

            actions.append({
                "name": generator_action.name,
                "display_name": display_name,
                "parameters": generator.get_parameters(generator_action)
            })

        generator_display_name = generator.get_generator_display_name(
            generator_name)

        response["generators"].append({
            "name": generator_name.name,
            "display_name": generator_display_name,
            "actions": actions
        })

    return response
