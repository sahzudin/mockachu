#!/usr/bin/env python3
"""
Mockachu - Complete Unified API Server

A comprehensive Flask-based REST API for generating mock data programmatically.
Combines all functionality from standalone, Swagger, and unified versions.
Designed for both standalone operation and desktop application integration.
"""

# Handle both standalone and embedded execution
from datetime import datetime
from flask_restx import Api, Resource, fields
from flask_cors import CORS
from flask import Flask, request, jsonify
from pathlib import Path
import csv
import io
import time
import threading
import sys
GeneratorFormats = None
get_available_generators = None
DataGenerator = None

try:
    # Try relative imports first (when run as module)
    from .generators.generator import GeneratorFormats
    from .services.available_generators import get_available_generators
    from .services.data_generator import DataGenerator
except ImportError:
    try:
        # Try absolute imports (when run standalone)
        from mockachu.generators.generator import GeneratorFormats
        from mockachu.services.available_generators import get_available_generators
        from mockachu.services.data_generator import DataGenerator
    except ImportError as e:
        print(
            f"Warning: Could not import some modules due to dependencies: {e}")
        print("Falling back to standalone mode...")


# Get package root for relative imports
package_root = Path(__file__).parent


class SimpleDataGenerator:
    """Simple standalone data generator without PyQt6 dependencies"""

    def __init__(self):
        from random import choice, randint

        self.choice = choice
        self.randint = randint

        # Try to import CustomListGenerator, fallback to None if not available
        try:
            from .generators.custom_list_generator import CustomListGenerator
            self.custom_list_generator = CustomListGenerator()
        except ImportError:
            try:
                from mockachu.generators.custom_list_generator import CustomListGenerator
                self.custom_list_generator = CustomListGenerator()
            except ImportError:
                self.custom_list_generator = None

        # Sample data
        self.first_names = ["John", "Jane", "Bob",
                            "Alice", "Charlie", "Diana", "Eve", "Frank"]
        self.last_names = ["Smith", "Johnson", "Williams",
                           "Brown", "Jones", "Garcia", "Miller", "Davis"]
        self.words = ["apple", "banana", "cherry", "dog",
                      "elephant", "forest", "guitar", "house"]

    def generate_data(self, fields, rows):
        """Generate mock data based on field configurations (legacy interface)"""
        return self.generate({
            "fields": fields,
            "rows": rows,
            "format": "JSON"
        })

    def generate(self, request):
        """Generate mock data based on request (main interface)"""
        fields = request["fields"]
        rows = request["rows"]

        result = []

        for _ in range(rows):
            record = {}
            for field in fields:
                value = self.generate_field_value(field)
                record[field['name']] = value
            result.append(record)

        return result

    def generate_field_value(self, field):
        """Generate a single field value"""
        generator = field.get('generator')
        action = field.get('action')
        parameters = field.get('parameters', [])

        # Handle enum or string types
        generator_name = generator.name if hasattr(
            generator, 'name') else str(generator)
        action_name = action.name if hasattr(action, 'name') else str(action)

        if generator_name == 'PERSON_GENERATOR':
            if action_name == 'RANDOM_PERSON_FIRST_NAME':
                return self.choice(self.first_names)
            elif action_name == 'RANDOM_PERSON_LAST_NAME':
                return self.choice(self.last_names)
            elif action_name == 'RANDOM_PERSON_AGE':
                return self.randint(18, 80)

        elif generator_name == 'STRING_GENERATOR':
            if action_name == 'RANDOM_STRING':
                length = 8
                chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                return ''.join(self.choice(chars) for _ in range(length))
            elif action_name == 'RANDOM_WORD':
                return self.choice(self.words)

        elif generator_name == 'CUSTOM_LIST_GENERATOR':
            if parameters and self.custom_list_generator:
                custom_list = parameters[0]
                if action_name == 'RANDOM_CUSTOM_LIST_ITEM':
                    return self.custom_list_generator._CustomListGenerator__generate_random_custom_list_item(custom_list)
                elif action_name == 'SEQUENTIAL_CUSTOM_LIST_ITEM':
                    return self.custom_list_generator._CustomListGenerator__generate_sequential_custom_list_item(custom_list)
            elif parameters:
                # Fallback when custom_list_generator is not available
                custom_list = parameters[0]
                if custom_list:
                    return self.choice(custom_list)

        return "sample_value"


class CompleteMockDataAPI:
    """Complete unified API class with all functionality"""

    def __init__(self, host='0.0.0.0', port=8843, debug=False):
        self.host = host
        self.port = port
        self.debug = debug
        self.app = Flask(__name__)
        self.server_thread = None
        self.is_running = False

        # Configure CORS
        CORS(self.app,
             origins="*",
             methods=["GET", "POST", "OPTIONS"],
             allow_headers=["Content-Type", "Authorization"])

        # Initialize Flask-RESTX API with comprehensive Swagger documentation
        self.api = Api(
            self.app,
            version='1.0.0',
            title='Mockachu API',
            description='''
A comprehensive REST API for generating realistic mock data programmatically. 
Perfect for development, testing, and prototyping applications.

## Features
- 🎲 Multiple data generators (Person, Cars, Text, Numbers, Geography, etc.)
- 📊 Multiple output formats (JSON, CSV, XML)
- 📖 Interactive Swagger documentation

## How to Use
1. Explore available generators at `/generators`
2. Copy request examples from the documentation below
3. Paste them into the "Try it out" sections in Swagger
4. Modify the parameters as needed
5. Execute to generate your mock data

This API fully supports clipboard integration and field configurations from the desktop application.
            ''',
            doc='/swagger/',
            contact_email='s.mahmic@live.com',
            contact_url='https://github.com/sahzudin/mockachu'
        )

        # Initialize services
        try:
            if GeneratorFormats is not None:
                self.data_generator = DataGenerator()
                self.available_generators = get_available_generators()
            else:
                raise ImportError("PyQt6 dependencies not available")
        except Exception as e:
            print(f"Warning: Could not load all generators - {e}")
            # Fallback to simplified generators
            self.data_generator = self.get_simple_data_generator()
            self.available_generators = self.get_simplified_generators()

        self.setup_models()
        self.setup_routes()
        self.setup_error_handlers()

    def get_simplified_generators(self):
        """Get a simplified list of generators for standalone operation"""
        return {
            "PERSON_GENERATOR": {
                "name": "Person Generator",
                "description": "Generate person-related data",
                "actions": {
                    "RANDOM_PERSON_FIRST_NAME": "Random first name",
                    "RANDOM_PERSON_LAST_NAME": "Random last name",
                    "RANDOM_PERSON_AGE": "Random age"
                }
            },
            "STRING_GENERATOR": {
                "name": "String Generator",
                "description": "Generate various string formats",
                "actions": {
                    "RANDOM_STRING": "Random string",
                    "RANDOM_WORD": "Random word"
                }
            },
            "CUSTOM_LIST_GENERATOR": {
                "name": "Custom List Generator",
                "description": "Generate items from custom lists",
                "actions": {
                    "RANDOM_CUSTOM_LIST_ITEM": "Random item from custom list",
                    "SEQUENTIAL_CUSTOM_LIST_ITEM": "Sequential item from custom list"
                }
            }
        }

    def get_simple_data_generator(self):
        """Create a simple data generator for standalone operation"""
        return SimpleDataGenerator()

    def setup_models(self):
        """Setup Swagger/OpenAPI models for documentation"""

        # Field configuration model
        self.field_model = self.api.model('Field', {
            'name': fields.String(
                required=True,
                description='Name of the field in the output',
                example='first_name'
            ),
            'generator': fields.String(
                required=True,
                description='Generator type to use',
                example='PERSON_GENERATOR'
            ),
            'action': fields.String(
                required=True,
                description='Specific action within the generator',
                example='RANDOM_PERSON_FIRST_NAME'
            ),
            'parameters': fields.List(
                fields.Raw,
                required=False,
                description='Parameters for the generator action (optional, varies by generator). Can contain strings, numbers, or mixed types.',
                example=[10, 'pattern', 100.5]
            )
        })

        # Generation request model
        self.generation_request = self.api.model('GenerationRequest', {
            'fields': fields.List(
                fields.Nested(self.field_model),
                required=True,
                description='List of field configurations'
            ),
            'rows': fields.Integer(
                required=False,
                description='Number of rows to generate',
                example=10,
                default=10
            ),
            'format': fields.String(
                required=False,
                description='Output format: JSON, CSV, or XML',
                example='JSON',
                default='JSON',
                enum=['JSON', 'CSV', 'XML']
            )
        })

        # Success response model
        self.success_response = self.api.model('SuccessResponse', {
            'data': fields.Raw(
                description='Generated data in the requested format'
            ),
            'metadata': fields.Raw(
                description='Generation metadata including timing and statistics'
            )
        })

        # Error response model
        self.error_response = self.api.model('ErrorResponse', {
            'error': fields.String(
                description='Error message',
                example='Invalid generator type'
            ),
            'details': fields.String(
                description='Detailed error information',
                example='Generator "INVALID_GENERATOR" not found'
            )
        })

        # Generator info model
        self.generator_info = self.api.model('GeneratorInfo', {
            'name': fields.String(description='Generator display name'),
            'description': fields.String(description='Generator description'),
            'actions': fields.Raw(description='Available actions for this generator')
        })

    def setup_routes(self):
        """Setup all API routes with comprehensive documentation"""

        # Create default namespace for clean URLs (no prefix)
        endpoints_ns = self.api.namespace('',
                                          description='Core API endpoints for data generation and service information')

        # Store reference to self for nested classes
        api_instance = self

        @endpoints_ns.route('/')
        class ApiRoot(Resource):
            def get(self):
                """API Information and Status

                Get basic information about the Mockachu API,
                including version, available endpoints, and quick start guide.

                Use this endpoint to understand how to interact with the API
                and get links to documentation and other resources.
                """
                return {
                    'name': 'Mockachu API',
                    'version': '1.0.0',
                    'description': 'Generate realistic mock data for development and testing',
                    'documentation': '/swagger/',
                    'repository': 'https://github.com/sahzudin/mockachu',
                    'endpoints': {
                        'root': '/ - API information (this endpoint)',
                        'health': '/health - Health check and server status',
                        'generators': '/generators - List all available generators',
                        'generate': '/generate - Generate mock data (POST)',
                        'swagger': '/swagger/ - Interactive API documentation'
                    },
                    'quick_start': {
                        'step_1': 'GET /generators to see available data types',
                        'step_2': 'POST /generate with your field configuration',
                        'step_3': 'Receive generated data in JSON, CSV, or XML format'
                    },
                    'custom_lists': {
                        'description': 'Support for custom data lists with clipboard integration',
                        'formats': ['comma-separated', 'semicolon-separated', 'newline-separated', 'mixed'],
                        'example': 'apple, banana; cherry\\ndate',
                        'swagger_usage': 'Copy request examples from documentation below and paste into Swagger "Try it out" sections'
                    }
                }

        @endpoints_ns.route('/health')
        class ApiHealth(Resource):
            def get(self):
                """Health Check

                Check if the API server is running properly and return system status.
                Useful for monitoring and load balancer health checks.

                Returns server status, uptime information, and configuration details.
                """
                return {
                    'status': 'healthy',
                    'timestamp': datetime.now().isoformat(),
                    'version': '1.0.0',
                    'server': {
                        'host': api_instance.host,
                        'port': api_instance.port,
                        'debug': api_instance.debug
                    },
                    'generators_loaded': len(api_instance.available_generators),
                    'uptime': 'running'
                }

        @endpoints_ns.route('/generators')
        class ApiGenerators(Resource):
            def get(self):
                """List Available Generators

                Get a complete list of all available data generators and their actions.
                Use this to understand what types of data you can generate.

                Each generator has multiple actions for different variations of data.
                Copy the generator and action names from this response to use in your
                /generate requests.
                """
                try:
                    # Handle both dictionary and list formats
                    if isinstance(api_instance.available_generators, dict):
                        if 'generators' in api_instance.available_generators:
                            # Format: {"generators": [...], "formats": [...]}
                            generators_list = api_instance.available_generators['generators']
                            formatted_generators = {}
                            for gen_info in generators_list:
                                gen_key = gen_info.get('name', 'unknown')
                                formatted_generators[gen_key] = {
                                    'name': gen_info.get('display_name', gen_key),
                                    'description': f'Generator for {gen_key}',
                                    'actions': {action['name']: action.get('display_name', action['name'])
                                                for action in gen_info.get('actions', [])}
                                }
                        else:
                            # Format: {generator_name: generator_info, ...}
                            formatted_generators = {}
                            for gen_key, gen_info in api_instance.available_generators.items():
                                formatted_generators[gen_key] = {
                                    'name': gen_info.get('name', gen_key),
                                    'description': gen_info.get('description', f'Generator for {gen_key}'),
                                    'actions': gen_info.get('actions', {})
                                }
                    else:
                        # Fallback for unexpected format
                        formatted_generators = {}

                    return {
                        'generators': formatted_generators,
                        'total_count': len(formatted_generators),
                        'timestamp': datetime.now().isoformat()
                    }
                except Exception as e:
                    api_instance.api.abort(
                        500, f'Error loading generators: {str(e)}')

        @endpoints_ns.route('/generate')
        class ApiGenerate(Resource):
            @self.api.expect(self.generation_request, validate=False)
            @self.api.marshal_with(self.success_response)
            @self.api.response(400, 'Bad Request', self.error_response)
            @self.api.response(500, 'Internal Server Error', self.error_response)
            def post(self):
                """Generate Mock Data

                Generate mock data based on your field configuration.

                ## How to Use This Endpoint

                1. **Copy Examples**: Copy the JSON examples below
                2. **Open Swagger**: Click "Try it out" button 
                3. **Paste & Modify**: Paste the example and modify as needed
                4. **Execute**: Click "Execute" to generate data

                ## Field Configuration
                Each field must specify:
                - **name**: The field name in the output
                - **generator**: The generator type (see /generators)
                - **action**: The specific action within that generator
                - **parameters**: Optional parameters (required for custom lists)

                ## Custom Lists
                For custom list generators, provide your data in the parameters array:
                ```json
                {
                  "name": "product",
                  "generator": "CUSTOM_LIST_GENERATOR", 
                  "action": "RANDOM_CUSTOM_LIST_ITEM",
                  "parameters": ["apple, banana, cherry; date\\ngrape"]
                }
                ```

                ## Output Formats
                - **JSON**: Structured data as JSON array
                - **CSV**: Comma-separated values with headers
                - **XML**: Simple XML structure

                ## Copy-Paste Examples

                ### Basic Person Data (Copy This!)
                ```json
                {
                  "fields": [
                    {"name": "first_name", "generator": "PERSON_GENERATOR", "action": "RANDOM_PERSON_FIRST_NAME"},
                    {"name": "age", "generator": "PERSON_GENERATOR", "action": "RANDOM_PERSON_AGE"}
                  ],
                  "rows": 5,
                  "format": "JSON"
                }
                ```

                ### Custom List Example (Copy This!)
                ```json
                {
                  "fields": [
                    {
                      "name": "fruit",
                      "generator": "CUSTOM_LIST_GENERATOR",
                      "action": "RANDOM_CUSTOM_LIST_ITEM", 
                      "parameters": ["apple, banana, cherry"]
                    }
                  ],
                  "rows": 3,
                  "format": "JSON"
                }
                ```

                ### Mixed Data Example (Copy This!)
                ```json
                {
                  "fields": [
                    {"name": "name", "generator": "PERSON_GENERATOR", "action": "RANDOM_PERSON_FIRST_NAME"},
                    {"name": "product", "generator": "CUSTOM_LIST_GENERATOR", "action": "RANDOM_CUSTOM_LIST_ITEM", "parameters": ["laptop, mouse, keyboard"]},
                    {"name": "description", "generator": "STRING_GENERATOR", "action": "RANDOM_WORD"}
                  ],
                  "rows": 10,
                  "format": "CSV"
                }
                ```
                """
                try:
                    data = request.get_json()

                    if not data:
                        api_instance.api.abort(400, 'No JSON data provided')

                    # Validate required fields
                    if 'fields' not in data:
                        api_instance.api.abort(
                            400, 'Missing "fields" in request')

                    if not isinstance(data['fields'], list) or len(data['fields']) == 0:
                        api_instance.api.abort(
                            400, 'Fields must be a non-empty array')

                    # Extract parameters
                    fields = data['fields']
                    rows = data.get('rows', 10)
                    format_type = data.get('format', 'JSON').upper()

                    # Validate rows
                    if not isinstance(rows, int) or rows <= 0:
                        api_instance.api.abort(
                            400, 'Rows must be a positive integer')

                    if rows > 10000:  # Reasonable limit
                        api_instance.api.abort(
                            400, 'Maximum 10,000 rows allowed')

                    # Validate format
                    if format_type not in ['JSON', 'CSV', 'XML']:
                        api_instance.api.abort(
                            400, 'Format must be JSON, CSV, or XML')

                    # Validate and convert field configurations
                    converted_fields = []
                    for i, field in enumerate(fields):
                        try:
                            converted_field = api_instance.convert_field_config(
                                field)
                            converted_fields.append(converted_field)
                        except Exception as e:
                            api_instance.api.abort(
                                400, f'Invalid field configuration at index {i}: {str(e)}')

                    # Generate data
                    start_time = time.time()

                    try:
                        # Convert the request format to match DataGenerator.generate
                        request_data = {
                            "fields": converted_fields,
                            "rows": rows,
                            "format": format_type
                        }
                        generated_data = api_instance.data_generator.generate(
                            request_data)
                    except Exception as e:
                        error_msg = f'Data generation failed: {str(e)}'
                        if 'custom_list' in str(e).lower():
                            error_msg += '. Check custom list format and ensure parameters are provided.'
                        api_instance.api.abort(500, error_msg)

                    generation_time = time.time() - start_time

                    # Format output
                    try:
                        formatted_data = api_instance.format_data(
                            generated_data, format_type)
                    except Exception as e:
                        api_instance.api.abort(
                            500, f'Data formatting failed: {str(e)}')

                    # Prepare response
                    response = {
                        'data': formatted_data,
                        'metadata': {
                            'rows_generated': len(generated_data) if isinstance(generated_data, list) else rows,
                            'generation_time_seconds': round(generation_time, 4),
                            'format': format_type,
                            'timestamp': datetime.now().isoformat(),
                            'field_count': len(converted_fields)
                        }
                    }

                    return response

                except Exception as e:
                    if hasattr(e, 'code'):  # Flask-RESTX abort
                        raise e
                    api_instance.api.abort(500, f'Unexpected error: {str(e)}')

    def convert_field_config(self, field_data):
        """Convert API field configuration to internal format"""
        if not isinstance(field_data, dict):
            raise ValueError('Field must be an object')

        required_keys = ['name', 'generator', 'action']
        for key in required_keys:
            if key not in field_data:
                raise ValueError(f'Missing required field: {key}')

        # Check if we have the full generator system or simplified mode
        try:
            # Try to import necessary classes
            from generators.generator import GeneratorType, GeneratorActions

            # Convert generator name to enum
            generator_name = field_data['generator']
            try:
                generator_enum = GeneratorType[generator_name]
            except KeyError:
                raise ValueError(f'Unknown generator: {generator_name}')

            # Convert action name to enum
            action_name = field_data['action']
            try:
                action_enum = GeneratorActions[action_name]
            except KeyError:
                raise ValueError(f'Unknown action: {action_name}')

            # Prepare field configuration with all required fields
            parameters = field_data.get('parameters', [])
            # Ensure parameters is always a list
            if not isinstance(parameters, list):
                parameters = [parameters] if parameters is not None else []

            converted_field = {
                'name': field_data['name'],
                'generator': generator_enum,
                'action': action_enum,
                'parameters': parameters,
                'nullable_percentage': 0  # Default: no nulls
            }

        except ImportError:
            # Fallback to simple string-based mode
            parameters = field_data.get('parameters', [])
            # Ensure parameters is always a list
            if not isinstance(parameters, list):
                parameters = [parameters] if parameters is not None else []

            converted_field = {
                'name': field_data['name'],
                'generator': field_data['generator'],  # Keep as string
                'action': field_data['action'],        # Keep as string
                'parameters': parameters,
                'nullable_percentage': 0  # Default: no nulls
            }

        return converted_field

    def format_data(self, data, format_type):
        """Format generated data according to the requested format"""
        if not data:
            return [] if format_type == 'JSON' else ''

        if format_type == 'JSON':
            return data

        elif format_type == 'CSV':
            if not isinstance(data, list) or not data:
                return ''

            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            return output.getvalue()

        elif format_type == 'XML':
            if not isinstance(data, list) or not data:
                return '<?xml version="1.0" encoding="UTF-8"?><data></data>'

            xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<data>']
            for item in data:
                xml_lines.append('  <record>')
                for key, value in item.items():
                    # Escape XML special characters
                    escaped_value = str(value).replace('&', '&amp;').replace(
                        '<', '&lt;').replace('>', '&gt;')
                    xml_lines.append(f'    <{key}>{escaped_value}</{key}>')
                xml_lines.append('  </record>')
            xml_lines.append('</data>')
            return '\n'.join(xml_lines)

        else:
            return data

    def setup_error_handlers(self):
        """Setup global error handlers"""

        @self.app.errorhandler(400)
        def handle_bad_request(e):
            return jsonify({
                'error': 'Bad Request',
                'details': str(e.description) if hasattr(e, 'description') else str(e),
                'timestamp': datetime.now().isoformat()
            }), 400

        @self.app.errorhandler(404)
        def handle_not_found(e):
            return jsonify({
                'name': 'Mockachu API',
                'version': '1.0.0',
                'error': 'Endpoint not found',
                'message': 'The requested endpoint does not exist. See available endpoints below.',
                'available_endpoints': {
                    'root': '/ - API information and status',
                    'health': '/health - Health check and server status',
                    'generators': '/generators - List all available data generators',
                    'generate': '/generate - Generate mock data (POST)',
                    'documentation': '/swagger/ - Interactive API documentation'
                },
                'quick_start': {
                    '1': 'Visit /swagger/ for interactive documentation',
                    '2': 'GET /generators to see available data types',
                    '3': 'POST /generate with your field configuration',
                    '4': 'Copy examples from Swagger and modify as needed'
                },
                'documentation_url': '/swagger/',
                'timestamp': datetime.now().isoformat()
            }), 404

        @self.app.errorhandler(500)
        def handle_internal_error(e):
            return jsonify({
                'error': 'Internal Server Error',
                'details': str(e.description) if hasattr(e, 'description') else 'An unexpected error occurred',
                'timestamp': datetime.now().isoformat()
            }), 500

    def start_threaded(self):
        """Start the server in a separate thread"""
        if self.is_running:
            return False

        def run_server():
            self.app.run(host=self.host, port=self.port,
                         debug=False, threaded=True, use_reloader=False)

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.is_running = True

        # Wait a moment for server to start
        time.sleep(1)
        return True

    def stop(self):
        """Stop the threaded server"""
        self.is_running = False
        if self.server_thread:
            self.server_thread.join(timeout=5)

    def run(self, host=None, port=None, debug=None):
        """Run the API server"""
        if host is not None:
            self.host = host
        if port is not None:
            self.port = port
        if debug is not None:
            self.debug = debug

        print("🚀 Starting Complete Mockachu API server...")
        print(f"📍 Server URL: http://{self.host}:{self.port}")
        print(
            f"📖 Swagger Documentation: http://{self.host}:{self.port}/swagger/")
        print(f"🔧 Debug mode: {'ON' if self.debug else 'OFF'}")
        print("="*60)
        print("Available endpoints:")
        print(f"  • GET  /              - API information and status")
        print(f"  • GET  /health        - Health check")
        print(f"  • GET  /generators    - List available generators")
        print(f"  • POST /generate      - Generate mock data")
        print(f"  • GET  /swagger/      - Interactive API documentation")
        print("="*60)
        print("🎯 Custom List Support:")
        print("  • Clipboard integration ready")
        print("  • Multiple format support (comma, semicolon, newline)")
        print("  • Sequential and random selection modes")
        print("="*60)

        try:
            self.app.run(host=self.host, port=self.port,
                         debug=self.debug, threaded=True)
        except KeyboardInterrupt:
            print("\n👋 Shutting down API server...")
        except Exception as e:
            print(f"❌ Error running server: {e}")
            raise


# Create a global app instance for embedded use
try:
    api_instance = CompleteMockDataAPI()
    app = api_instance.app
except Exception as e:
    print(f"Warning: Could not create global API instance: {e}")
    app = None


def main():
    """Main entry point for the complete unified API server"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Complete Mockachu API Server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python api_server_unified_complete.py                    # Run with default settings
  python api_server_unified_complete.py --port 8080        # Run on port 8080
  python api_server_unified_complete.py --debug            # Run in debug mode
  python api_server_unified_complete.py --host 127.0.0.1   # Run on localhost only

Features:
  ✅ Complete Swagger/OpenAPI documentation
  ✅ Custom list generator with clipboard support
  ✅ Multiple output formats (JSON, CSV, XML)
  ✅ Comprehensive error handling
  ✅ Desktop application integration
  ✅ Standalone operation capability

Once running, visit http://localhost:8843/swagger/ for interactive API documentation.
        """
    )

    parser.add_argument('--host', default='0.0.0.0',
                        help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8843,
                        help='Port to bind to (default: 8843)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode for development')

    args = parser.parse_args()

    try:
        api = CompleteMockDataAPI()
        api.run(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\n👋 Shutting down API server...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
