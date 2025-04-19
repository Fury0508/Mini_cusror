import unittest
from app import app

class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_register(self):
        response = self.app.post('/register', data=dict(username='testuser', password='testpass'))
        self.assertEqual(response.status_code, 302)  # Redirects to login

    def test_login(self):
        self.app.post('/register', data=dict(username='testuser', password='testpass'))
        response = self.app.post('/login', data=dict(username='testuser', password='testpass'))
        self.assertEqual(response.status_code, 302)  # Redirects to home

    def test_adding_todo_requires_login(self):
        response = self.app.post('/add_todo', data=dict(todo='Test Todo'))
        self.assertEqual(response.status_code, 302)  # Redirects to login (not logged in)

    def test_add_todo(self):
        self.app.post('/register', data=dict(username='testuser', password='testpass'))
        self.app.post('/login', data=dict(username='testuser', password='testpass'))
        response = self.app.post('/add_todo', data=dict(todo='Test Todo'))
        self.assertEqual(response.status_code, 302)  # Redirects to home

    def test_access_todolist_after_login(self):
        self.app.post('/register', data=dict(username='testuser', password='testpass'))
        self.app.post('/login', data=dict(username='testuser', password='testpass'))
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Todo List', response.data)

if __name__ == '__main__':
    unittest.main()