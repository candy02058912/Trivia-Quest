import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.mock_question = {
            'question': 'mock question',
            'answer': 'mock answer',
            'category': 1,
            'difficulty': 2,
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_questions(self):
        res = self.client().get('/questions')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertLessEqual(len(data['questions']), 10)
        self.assertTrue(data)

    def test_get_questions_fail(self):
        res = self.client().get('/questions?page=0')
        self.assertEqual(res.status_code, 404)
        data = json.loads(res.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 404)

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertLessEqual(len(data['questions']), 10)
        self.assertTrue(data)

    def test_get_questions_by_category_fail(self):
        res = self.client().get('/categories/1/questions?page=0')
        self.assertEqual(res.status_code, 404)
        data = json.loads(res.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 404)

    def test_get_categories(self):
        res = self.client().get('/categories')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data)

    def test_create_question(self):
        mock_pass_question = self.mock_question
        res = self.client().post('/questions', json=mock_pass_question)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])

    def test_create_question_fail(self):
        mock_fail_question = {
            'question': 'mock question',
            'answer': 'mock answer',
            'difficulty': 2,
        }
        res = self.client().post('/questions', json=mock_fail_question)
        self.assertEqual(res.status_code, 422)
        data = json.loads(res.data)
        self.assertFalse(data['success'])

    def test_search_question(self):
        search_request = {
            'searchTerm': 'mock'
        }
        res = self.client().post('/questions/search', json=search_request)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertGreaterEqual(len(data['questions']), 1)

    def test_search_question_empty_result(self):
        search_request = {
            'searchTerm': 'empty result keyword'
        }
        res = self.client().post('/questions/search', json=search_request)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(len(data['questions']), 0)

    def test_delete_question(self):
        res = self.client().post('/questions', json=self.mock_question)
        data = json.loads(res.data)
        question_id = data['question_id']
        res = self.client().delete('/questions/{}'.format(question_id))
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])

    def test_quiz(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category':
            {'type': 'Any', 'id': '1'}
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_quiz_fail(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category':
            {'type': 'Error', 'id': 'Error'}
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
