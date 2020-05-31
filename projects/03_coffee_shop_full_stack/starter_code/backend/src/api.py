import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from werkzeug.exceptions import NotFound,BadRequest
from jose import jwt
import base64

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

AUTH0_DOMAIN = "raj-udacity.auth0.com"
API_AUDIENCE = "https://raj-udacity.auth0.com/api/v2/"
ALGORITHMS = ['RS256']

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()
## ROUTES

@app.route('/drinks',methods = ['GET'])
def get_drinks():
    drinks = Drink.query.all()
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    })


@app.route('/drinks-detail',methods = ['GET'])
@requires_auth("get:drinks-detail")
def get_drink_details():
    drinks = Drink.query.all()
    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    })

@app.route('/drinks',methods = ['POST'])
@requires_auth("post:drinks")
def add_drinks():
    body = request.get_json()
    recipe = body['recipe']
    if not isinstance(recipe,list):
        raise BadRequest
    
    drink_title = body['title']
    recipe = json.dumps(recipe)
    drink = Drink(title=drink_title,recipe=recipe)
    drink.insert()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


@app.route('/drinks/<int:id>',methods = ['PATCH'])
@requires_auth("patch:drinks")
def change_drink(id):
   
    drink = Drink.query.get(id)
    if not drink:
        raise NotFound 
    
    body = request.get_json()
    title = body.get('title',None)
    recipe = body.get('recipe',None)
    
    if title:
        drink.title = title
    if recipe and isinstance(recipe,list):
        drink.recipe = json.dumps(recipe)

    drink.update()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


@app.route('/drinks/<int:id>',methods=['DELETE'])
@requires_auth("delete:drinks")
def delete_drink(id):
    drink = Drink.query.get(id)

    if not drink:
        raise NotFound 
       
    drink.delete()

    return jsonify({
        'success': True,
        'delete': id
    })

## Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def notfound(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404


@app.errorhandler(400)
def badrequest(error):
    return jsonify({
                    "success": False, 
                    "error": 400,
                    "message": "bad request"
                    }), 400


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

@app.errorhandler(500)
def servererror(error):
    return jsonify({
                    "success": False, 
                    "error": 500,
                    "message": "internal server error"
                    }), 500

