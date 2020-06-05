import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
import random

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            'postgres:postgres@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
            for x in range(0, 3):
                self.createCategory(x)
                self.createQuestion()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def createCategory(self, id):
        if Category.query.count() < 3:
            categories = ["Science", "Art", "Sports"]
            category = Category(categories[id])
            category.insert()

    def createQuestion(self):
        if Question.query.count() < 3:
            categories = Category.query.all()
            difficulty = random.randrange(1, 4)
            category = random.choice(categories)
            question = Question(question="testing question",
                                answer="testing answer",
                                category=category.id, difficulty=difficulty)
            question.insert()

    # getting categories test

    def test_get_categories(self):
        res = self.client().get('/categories')
        self.assertEqual(res.status_code, 200)

    # getting questions test
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['current_category'], '')

    # deleting question tests

    def test_delete_question(self):
        question_to_delete = Question.query.first()
        res = self.client().delete(f'/questions/{question_to_delete.id}')
        data = json.loads(res.data)

        question = Question.query.filter(
            Question.id == question_to_delete.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['status'], 'Success')
        self.assertEqual(question, None)

    def test_delete_question_notfound(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 500)
        self.assertEqual(data['status'], "Failure")

    # creating questions test

    def test_create_question(self):
        categories = Category.query.all()
        category = random.choice(categories)
        res = self.client().post('/questions', json={
            "answer": "Maya Angelou",
            "category": category.id,
            "difficulty": 2,
            "question": "'I Know Why the Caged Bird Sings'?"
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['status'], "Success")

    def test_create_question_missing_info(self):
        res = self.client().post('/questions', json={
            "answer": "Maya Angelou",
            "difficulty": 2,
            "question": "'I Know Why the Caged Bird Sings'?"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['status'], "Failure")

    # creating question search test
    def test_question_search(self):
        res = self.client().post('/questions/search', json={"searchTerm": "e"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], '')

    def test_question_search_no_results(self):
        res = self.client().post('/questions/search',
                                 json={"searchTerm": "winning"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(data['current_category'], '')

    # creating questions by catgory test
    def test_get_questions_by_category(self):
        questions = Question.query.all()
        question = random.choice(questions)
        res = self.client().get(f'/categories/{question.category}/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_get_questions_by_invalid_category(self):
        res = self.client().get('/categories/30/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['status'], "Failure")

    # def test_get_questions_for_quiz(self):


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
