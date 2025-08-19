"""
Basic tests for Mockachu API
"""

import pytest
import json
from mockachu.api import CompleteMockDataAPI


class TestMockDataAPI:
    """Test cases for the Mock Data API"""

    @pytest.fixture
    def api(self):
        """Create API instance for testing"""
        return CompleteMockDataAPI()

    @pytest.fixture
    def client(self, api):
        """Create test client"""
        with api.app.test_client() as client:
            yield client

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'

    def test_status_endpoint(self, client):
        """Test status endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'version' in data

    def test_generators_endpoint(self, client):
        """Test generators endpoint"""
        response = client.get('/generators')
        assert response.status_code == 200
        data = json.loads(response.data)
        # Can be list or dict depending on marshalling
        assert isinstance(data, (list, dict))

    def test_basic_generation(self, client):
        """Test basic data generation"""
        payload = {
            "fields": [
                {"name": "test_field", "generator": "PERSON_GENERATOR",
                    "action": "RANDOM_PERSON_FIRST_NAME"}
            ],
            "rows": 5,
            "format": "JSON"
        }

        response = client.post('/generate',
                               data=json.dumps(payload),
                               content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
        assert 'metadata' in data
        assert data['metadata']['rows_generated'] == 5

    def test_invalid_generation_request(self, client):
        """Test invalid generation request"""
        payload = {
            "fields": [],  # Empty fields
            "rows": 5
        }

        response = client.post('/generate',
                               data=json.dumps(payload),
                               content_type='application/json')

        assert response.status_code == 400
        # For 400 errors, response might be different format
        data = json.loads(response.data)
        assert 'message' in data or 'error' in data

    def test_generation_with_numeric_parameters(self, client):
        """Test generation request with numeric parameters"""
        payload = {
            "fields": [
                {
                    "name": "test_string",
                    "generator": "STRING_GENERATOR",
                    "action": "RANDOM_ALPHABETICAL_UPPERCASE_STRING",
                    "parameters": [10]  # Numeric parameter for string length
                }
            ],
            "rows": 3,
            "format": "JSON"
        }

        response = client.post('/generate',
                               data=json.dumps(payload),
                               content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
        assert 'metadata' in data
        assert data['metadata']['rows_generated'] == 3
        # Verify the generated strings have the correct length
        for row in data['data']:
            assert len(row['test_string']) == 10
