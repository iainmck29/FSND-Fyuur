import os
from flask import Flask, request, abort, jsonify, flash, redirect, url_for
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_selection(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = page + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={r"/*": {'origins': '*'}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,True')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def get_all_categories():

        categories = Category.query.order_by(Category.id).all()
        current_categories = {}
        for category in categories:
            current_categories[category.id] = category.type

        if len(categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': current_categories
        })

    @app.route('/questions')
    def get_all_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_selection(request, selection)

        if len(current_questions) == 0:
            abort(404)

        categories_query = Category.query.order_by(Category.id).all()
        categories = {}
        for category in categories_query:
            categories[category.id] = category.type

        return jsonify({
            'success': True,
            'questions': current_questions,
            'categories': categories,
            'total_questions': len(current_questions),
            'current_category': None

        })

    @app.route('/questions/<question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                'success': True,
                'deleted': question_id
            })

        except:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()
        print(body)

        question = body.get('question', None)
        answer = body.get('answer', None)
        category = body.get('category', None)
        difficulty = body.get('difficulty', None)
        search_term = body.get('searchTerm', None)

        try:
            if search_term:
                selection = Question.query.filter(
                    Question.question.ilike('%{}%'.format(search_term)))
                current_questions = paginate_selection(request, selection)

                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(selection.all()),
                })
            else:

                new_question = Question(
                    question=question, answer=answer, category=category, difficulty=difficulty)

                new_question.insert()

                return jsonify({
                    'success': True
                })
        except:
            abort(422)

    @app.route('/categories/<category_id>/questions')
    def get_questions_by_category(category_id):
        selection = Question.query.filter(Question.category == category_id)
        questions = paginate_selection(request, selection)

        if len(questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': questions,
            'total_questions': len(selection.all()),
            'current_category': category_id
        })

    @app.route('/quizzes', methods=['POST'])
    def get_quiz_question():
        data = request.get_json()
        print(data)
        category = data.get('quiz_category')['id']

        previous_questions = data.get('previous_questions')
        if category is None:
            abort(404)

        if category == 0:
            new_question = Question.query.filter(
                Question.id.notin_(previous_questions)).first_or_404()
            new_question = new_question.format()
        else:
            new_question = Question.query.filter(
                Question.category == category, Question.id.notin_(previous_questions)).first_or_404()
            new_question = new_question.format()

        previous_questions.append(new_question['id'])
        return jsonify({
            'success': True,
            'previous_questions': previous_questions,
            'question': new_question,
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    return app
