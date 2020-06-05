import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound, UnprocessableEntity

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app)

    @app.after_request
    def access_control_allow(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            categories = {
                'categories': list(map(lambda x: x.type, Category.query.all()))
            }
            return jsonify(categories)
        except Exception:
            raise InternalServerError

    @app.route('/questions', methods=['GET'])
    def get_questions():
        page = request.args.get('page', 1, type=int)
        question_query = Question.query.paginate(
            page, QUESTIONS_PER_PAGE, False)
        question_items = [question.format()
                          for question in question_query.items]
        total_questions = question_query.total
        categories = [category.type for category in Category.query.all()]
        return jsonify({
            'questions': question_items,
            'total_questions': total_questions,
            'categories': categories,
            'current_category': ''
        })

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):

        try:
            question = Question.query.get(id)
            if not question:
                raise NotFound
            question.delete()
        except Exception:
            raise InternalServerError
        return jsonify({
            "status": 'Success'
        })

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        question = body.get('question', None)
        answer = body.get('answer', None)
        difficulty = int(body.get('difficulty', 0))
        category = body.get('category', None)

        if not question or not answer or difficulty < 1 or not category:
            raise BadRequest

        try:
            question = Question(question, answer, category, difficulty)
            question.insert()
        except Exception:
            raise InternalServerError

        return jsonify({
            "status": 'Success'
        })

    @app.route('/questions/search', methods=['POST'])
    def question_search():
        body = request.get_json()
        search_term = body.get('searchTerm', '')

        page = request.args.get('page', 1, type=int)

        query = '%' + search_term + '%'

        questions_page = Question.query.filter(Question.question.ilike(
            query)).paginate(page, QUESTIONS_PER_PAGE, False)

        questions = questions_page.items
        questions_formatted = [question.format() for question in questions]

        return jsonify({
            'questions': questions_formatted,
            'total_questions': questions_page.total,
            'current_category': ''
        })

    @app.route('/categories/<id>/questions', methods=['GET'])
    def get_questions_by_category(id):

        category = Category.query.get(id)

        if not category:
            raise NotFound

        question_by_category = Question.query.filter(
            Question.category == id).all()
        question_by_category_formatted = [
            question.format() for question in question_by_category]

        total_questions = len(question_by_category_formatted)

        category_formatted = category.format() if category else ''

        return jsonify({
            "questions": question_by_category_formatted,
            "total_questions": total_questions,
            "current_category": category_formatted
        })

    @app.route('/quizzes', methods=['POST'])
    def get_questions_for_quiz():
        body = request.get_json()
        previous_questions = body.get('previous_questions', '')
        quiz_category = body.get('quiz_category', '')

        if not quiz_category:
            quiz_category_id = 0
        else:
            quiz_category_id = int(quiz_category.get('id', 0))

        question_filter_query = Question.query.filter(
            Question.category == quiz_category_id)

        if quiz_category_id == 0:
            question_filter_query = Question.query

        questions = question_filter_query.filter(
            Question.id.notin_(previous_questions)).all()

        questions_formatted = [question.format() for question in questions]

        return jsonify({
            "question": random.choice(questions_formatted)
        })

    @app.errorhandler(BadRequest)
    def bad_request_handler(error):
        return jsonify({
            'status': 'Failure'
        }), 400

    @app.errorhandler(NotFound)
    def not_found_handler(error):
        return jsonify({
            'status': 'Failure'
        }), 404

    @app.errorhandler(UnprocessableEntity)
    def unprocessable_handler(error):
        return jsonify({
            'status': 'Failure'
        }), 422

    @app.errorhandler(InternalServerError)
    def internal_server_error_handler(error):
        return jsonify({
            'status': 'Failure'
        }), 500

    return app
