from app import create_app
import json
import unittest

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_health_data_endpoint(self):
        response = self.client.get('/api/healthdata')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(json.loads(response.data), list)

    def test_protected_health_data_endpoint(self):
        response = self.client.get('/api/healthdata/protected')
        self.assertEqual(response.status_code, 401)

    def test_post_health_data(self):
        response = self.client.post('/api/healthdata', json={'data': 'sample data'})
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', json.loads(response.data))

if __name__ == '__main__':
    unittest.main()