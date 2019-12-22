import os
from random import choice
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={'/': {'origins': '*'}})
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Origin',
                             '*')
        return response

    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        formatted_categories = {
            category.id: category.type for category in categories}

        return jsonify({
            "categories": formatted_categories,
        })

    @app.route('/questions')
    def get_questions():
        page = request.args.get('page', 1, type=int)
        questions = Question.query.paginate(page, QUESTIONS_PER_PAGE)
        categories = Category.query.all()
        formatted_categories = {
            category.id: category.type for category in categories}

        return jsonify({
            "success": True,
            "questions": [question.format() for question in questions.items],
            "total_questions": questions.total,
            "categories": formatted_categories,
            'current_category': None
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(
            Question.id == question_id).one_or_none()
        try:
            question.delete()
            return jsonify({
                "success": True,
            })
        except:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def create_question():
        data = request.get_json()
        try:
            question = Question(question=data['question'], answer=data['answer'],
                                difficulty=data['difficulty'], category=data['category'])
            question.insert()
            return jsonify({
                "success": True,
                "question_id": question.id
            })
        except:
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        data = request.get_json()
        search_query = data['searchTerm']
        questions = Question.query.filter(
            Question.question.ilike('%{}%'.format(search_query))).all()
        return jsonify({
            "success": True,
            'questions': [question.format() for question in questions]
        })

    @app.route('/categories/<string:category_id>/questions')
    def get_category_questions(category_id):
        page = request.args.get('page', 1, type=int)
        questions = Question.query.filter(
            Question.category == category_id).paginate(page, QUESTIONS_PER_PAGE)

        return jsonify({
            "success": True,
            "questions": [question.format() for question in questions.items],
            "total_questions": questions.total,
            'current_category': category_id
        })

    @app.route('/quizzes', methods=['POST'])
    def get_quiz():
        data = request.get_json()
        previous_questions = data.get('previous_questions')
        category = data.get('quiz_category', None)

        if category['id'] == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter(
                Question.category == category['id']).all()

        if not questions:
            abort(404)

        remaining_questions = [question.format()
                               for question in questions if question.format()['id'] not in previous_questions]

        try:
            question = choice(remaining_questions)
            return jsonify({
                'success': True,
                'question': choice(remaining_questions)
            })
        except:
            return jsonify({
                'success': True,
                'question': False
            })

    @app.errorhandler(400)
    def page_not_found(e):
        return jsonify(error=400, text=str(e), success=False), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify(error=404, text=str(e), success=False), 404

    @app.errorhandler(422)
    def unprocessable_entity(e):
        return jsonify(error=422, text=str(e), success=False), 422

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify(error=500, text=str(e), success=False), 500

    return app
