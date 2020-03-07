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
@uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
implements endpoint
    GET /drinks
        - public endpoint
        - contains only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def drinks():
    try:
        get_drinks = Drink.query.all()
        if len(drinks) == 0:
            abort(404)
        drinks = [drink.short for drink in get_drinks]

        return jsonify({
            "success": True,
            "drinks", drinks
        }), 200
    except:
        abort(401)

'''
implements endpoint
    GET /drinks-detail
        - requires the 'get:drinks-detail' permission
        - contains the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drink_details(payload):
    retrieve_drinks = Drink.query.all()
    if len(retrieve_drinks) == 0:
        abort(404)
    retrieve_drinks = [drink.long() for drink in retrieve_drinks]

    return jsonify({
        "success": True,
        "drinks": drinks,
    }), 200

'''
implements endpoint
    POST /drinks
        - creates a new row in the drinks table
        - requires the 'post:drinks' permission
        - contains the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(token):
    body = request.get_json()

    req_title = body.get('title', None)
    req_recipe = body.get('recipe', None)
    try:
        drink = Drink(title=req_title, recipe=req_recipe)
        drink.insert()
        drink = Drink.query.filter_by(id=drink.id).first()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 201
    except:
        abort(422)

'''
implements endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        - responds with a 404 error if <id> is not found
        - updates the corresponding row for <id>
        - requires the 'patch:drinks' permission
        - contains the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    try:
        body = request.get_json()
        patch_title = body.get('title')
        patch_recipe = body.get('recipe')
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            abort(404)

        drink.title = patch_title
        drink.recipe = patch_recipe
        drink.update()

        return jsonify({
            "success": True,
            "drinks": [drink.long()],
        }), 200
    except:
        abort(422)


'''
implements endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        - responds with a 404 error if <id> is not found
        - deletes the corresponding row for <id>
        - requires the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    try:
        drink = Drink.query.filter(Drink.id == id, title=req_title, recipe=req_recipe).one_or_none()
        if drink is None:
            abort(404)

        drink.delete()
        return jsonify({
            "success": True,
            "delete": id,
        }), 200
    except:
        abort(422)



# --------- Error Handlers ---------------------
'''
error handler for 422 unprocessable.
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
error handler for 404 not found.
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "not found"
    }), 404

'''
error handler for 400 bad request.
'''
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

'''
error handler for 405 method not allowed.
'''
@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error, please check."
    }), 500



'''
implements error handler for AuthError
'''
@app.errorhandler(AuthError)
def auth_error(auth_error):
    return jsonify({
        "success": False,
        "error": auth_error.status_code,
        "message": auth_error.error
    }), auth_error.status_code
