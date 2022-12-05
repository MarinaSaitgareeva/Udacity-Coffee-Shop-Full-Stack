try:
    # 👇️ using Python 3.10+
    from collections.abc import Iterable
except ImportError:
    # 👇️ using Python 3.10-
    from collections import Iterable

import collections.abc

# 👇️ add attributes to `collections` module
# before you import the package that causes the issue
collections.Iterable = collections.abc.Iterable
collections.Mapping = collections.abc.Mapping
collections.MutableMapping = collections.abc.MutableMapping
collections.MutableSet = collections.abc.MutableSet
collections.Callable = collections.abc.Callable

from flask import (
    Flask,
    request,
    jsonify,
    abort
)
import json
from flask_cors import CORS

from .database.models import (
    db_drop_and_create_all,
    setup_db,
    Drink
)
from .auth.auth import AuthError, requires_auth


app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
with app.app_context():
    db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=["GET"])
def retrieve_drinks():
    drinks = Drink.query.order_by(Drink.title).all()

    if len(drinks) == 0:
        abort(404)

    return jsonify({
        "success": True,
        "drinks": [drink.short() for drink in drinks]
    }), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks-detail", methods=["GET"])
@requires_auth("get:drinks-detail")
def retrieve_drink_detail(payload):
    drinks = Drink.query.order_by(Drink.title).all()

    if len(drinks) == 0:
        abort(404)

    return jsonify({
        "success": True,
        "drinks": [drink.long() for drink in drinks]
    }), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def create_drink(payload):
    body = request.get_json()

    if not ("title" in body or "recipe" in body):
        abort(422)

    title = body.get("title", None)
    recipe = body.get("recipe", None)

    try:
        # json.dumps() function will convert
        # a subset of Python objects into a json string
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200

    except Exception:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<int:drink_id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def modify_drink(payload, drink_id):
    body = request.get_json()

    if not ("title" in body or "recipe" in body):
        abort(422)

    title = body.get("title", None)
    recipe = body.get("recipe", None)

    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        drink.title = title
        drink.recipe = json.dumps(recipe)

        drink.update()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200

    except Exception:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(payload, drink_id):
    try:
        drink = drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
            "success": True,
            "delete": drink_id
        }), 200

    except Exception as e:
        print(e)
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable resource"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method Not Allowed"
    }), 405


@app.errorhandler(500)
def internal_server(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal server error"
    }), 500


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def handle_auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error["description"]
    }), error.status_code
