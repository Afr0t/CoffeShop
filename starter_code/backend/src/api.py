import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
setup_db(app)
CORS(app)

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,true")
    response.headers.add("Access-Control-Allow-Methods", "GET,PATCH,POST,DELETE,OPTIONS")
    return response

def validate_recipes(recipes):
    
    drink_recipes=[]
    if(not isinstance(recipes,list) and not isinstance(recipes,dict)):
        return None
    if(isinstance(recipes,dict)):
        try:
            name = recipes['name']
            parts = recipes['parts']
            color = recipes['color']
            if( not isinstance(name,str)):
                return None
            if( not isinstance(color,str)):
                return None
            if( not isinstance(parts,(str,int,float))):
                return None
            drink_recipes =  [{"color":color,"name":name,"parts":int(parts)}]
        except:
            return None
    else:
        for recipe in recipes:
            name = recipe['name']
            parts = recipe['parts']
            color = recipe['color']
            if( not isinstance(name,str)):
                return None
            if( not isinstance(color,str)):
                return None
            if( not isinstance(parts,(str,int,float))):
                return None
            drink_recipes.append({"color":color,"name":name,"parts":int(parts)})
    return drink_recipes

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks',methods=['GET'])
def get_drinks():
    '''
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
    '''
    drinks = Drink.query.order_by(Drink.id).all()
    print(drinks)
    return jsonify({
            'success':True,
            'drinks':[drink.short() for drink in drinks]
            })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail',methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_details(payload): 
    drinks = Drink.query.order_by(Drink.id).all()
    return jsonify({
            'success':True,
            'drinks':[drink.long() for drink in  drinks]
            })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    body = request.get_json()
    drink = Drink.query.get(id)

    if drink is None:
        abort(404)

    try:
        title = body.get('title')
        recipes = body.get('recipe')
        if title is not None:
            drink.title = title

        if recipes is not None :
            drink_recipes = validate_recipes(recipes)
            if(drink_recipes is not None):
                drink.recipes = json.dumps(drink_recipes)


        drink.update()
        return jsonify({
          'success':True,
          'drinks': [drink.long()]
              })
    except:
        abort(400)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(payload, id):
    body = request.get_json()
    drink = Drink.query.get(id)

    if drink is None:
        abort(404)

    try:
        title = body.get('title')
        recipes = body.get('recipe')
        if title is not None:
            drink.title = title

        if recipes is not None :
            drink_recipes = validate_recipes(recipes)
            if(drink_recipes is not None):
                drink.recipes = json.dumps(drink_recipes)


        drink.update()
        return jsonify({
          'success':True,
          'drinks': [drink.long()]
              })
    except:
        abort(400)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.get(id)

    if drink is None:
        abort(404)

    try:
        drink.delete()
    except:
        abort(500)

    return jsonify({
          'success':True,
          'delete': id
              })


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
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
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400    

@app.errorhandler(401)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Not Authorized"
    }), 401        

@app.errorhandler(403)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden"
    }), 403

@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500

    
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def handle_AuthException(e):
    return jsonify({
      "success": False, 
      "error": e.status_code,
      "message": e.error
      }), e.status_code
    

@app.errorhandler(HTTPException)
def handle_HttpException(e):
    return jsonify({
      "success": False, 
      "error": e.code,
      "message": e.name
      }), e.code