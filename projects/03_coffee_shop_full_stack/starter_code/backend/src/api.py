import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES


@app.route('/drinks')
def get_drinks():
    drinks_query = Drink.query.all()

    drinks = [drink.short() for drink in drinks_query]

    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks_query = Drink.query.all()

    drinks = [drink.long() for drink in drinks_query]

    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    body = request.get_json()
    print(body)

    title = body.get('title', None)
    recipe = body.get('recipe', None)

    try:
        if title == None or recipe == None:
            abort(422)
        else:
            new_drink = Drink(title=title,
                              recipe=json.dumps(recipe))
            new_drink.insert()

    except Exception as e:
        print(e)
        abort(403)

    return jsonify({
        "success": True,
        "drinks": [new_drink.long()]
    })


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    body = request.get_json()
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)

    try:
        if 'title' in body:
            new_title = body.get('title', None)
            # Should name in recipe also be updated?
            drink.title = new_title

        elif 'recipe in body':
            new_recipe = body.get('recipe')
            drink.recipe = new_recipe

        drink.update()
    except Exception as e:
        print(e)
        abort(403)

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)

    try:
        drink.delete()

    except Exception as e:
        print(e)
        abort(403)

    return jsonify({
        "success": True,
        "delete": id
    })


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(AuthError)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": "unprocessable"
    }), 422


@app.errorhandler(AuthError)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": "bad request"
    }), 400


@app.errorhandler(AuthError)
def unauthorised(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": "unauthorised"
    }), 401


@app.errorhandler(AuthError)
def not_found(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def unauthorised(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": "permission denied"
    }), 403


# '''
# @TODO implement error handlers using the @app.errorhandler(error) decorator
#     each error handler should return (with approprate messages):
#              jsonify({
#                     "success": False,
#                     "error": 404,
#                     "message": "resource not found"
#                     }), 404

# '''

# '''
# @TODO implement error handler for 404
#     error handler should conform to general task above
# '''
# '''
# @TODO implement error handler for AuthError
#     error handler should conform to general task above
# '''
