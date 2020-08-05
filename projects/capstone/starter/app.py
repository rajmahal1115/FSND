import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound, UnprocessableEntity

from models import setup_db, Actor, Movie, Gender
from auth import AuthError, requires_auth 

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # get a single actor
    @app.route('/actors/<int:id>', methods=['GET'])
    @requires_auth("get:actors")
    def get_actor(id):
        actor = Actor.query.get(id)
        if not actor:
            raise NotFound
        else: 
            return jsonify({'actor': actor.format()})

    # get all actors
    @app.route('/actors', methods=['GET'])
    @requires_auth("get:actors")
    def get_actors():
        try:
            actors = Actor.query.all()
            return jsonify({'actors': [actor.format() for actor in actors]})
        except Exception as e:
            raise InternalServerError

    # get all movies
    @app.route('/movies', methods=['GET'])
    @requires_auth("get:movies")
    def get_movies():
        try:
            movies = Movie.query.all()
            return jsonify({'movies': [movie.format() for movie in movies]})
        except Exception:
            raise InternalServerError

    # delete a single actor by id
    @app.route('/actors/<int:id>', methods=['DELETE'])
    @requires_auth("delete:actors")
    def delete_actor(id):
        actor = Actor.query.get(id)
        if not actor:
            raise NotFound
        try:
            actor.delete()
        except Exception as e:
            raise InternalServerError
        return jsonify({
            'status': 'Success'
        })

    # delete a single movie by id
    @app.route('/movies/<int:id>', methods=['DELETE'])
    @requires_auth("delete:movies")
    def delete_movie(id):
        movie = Movie.query.get(id)
        if not movie:
            raise NotFound
        try:
            movie.delete()
        except Exception:
            raise InternalServerError
        return jsonify({
            'status': 'Success'
        })

	# add an actor
    @app.route('/actors', methods=['POST'])
    @requires_auth("post:actors")
    def create_actor():
        body = request.get_json()
        name = body.get('name')
        age = body.get('age')
        gender = body.get('gender')
        
        if not name or not age or not gender:
            raise BadRequest
        try:
            actor = Actor(name, age, Gender[gender])
            actor.insert()
        except Exception as e:
            raise InternalServerError

        return jsonify({
            'status': 'Success'
        })

    # add a movie
    @app.route('/movies', methods=['POST'])
    @requires_auth("post:movies")
    def create_movie():
        body = request.get_json()
        title = body.get('title')
        releaseDate = body.get('releaseDate')

        if not title or not releaseDate:
            raise BadRequest
		
        try:
            movie = Movie(title,releaseDate)
            movie.insert()
        except Exception:
	        raise InternalServerError
        return jsonify({ 'status': 'Success'})

	# update an actor
    @app.route('/actors/<int:id>', methods=['PATCH'])
    @requires_auth("patch:actors")
    def update_actor(id):
        actor = Actor.query.get(id)
        if not actor:
            raise NotFound
		
        body = request.get_json()
        name = body.get('name',None)
        age = body.get('age',None)
        gender = body.get('gender',None)

        if name:
            actor.name = name
        if age:
            actor.age = age
        if gender:
	        actor.gender = Gender[gender]
        try:
            actor.update()
        
        except Exception:
	        raise InternalServerError
        
        return jsonify({
        'status': 'Success',
        'actor': actor.format() 
    	})

	# update a movie
    @app.route('/movies/<int:id>', methods=['PATCH'])
    @requires_auth("patch:movies")
    def update_movie(id):
        movie = Movie.query.get(id)
        if not movie:
            raise NotFound

        body = request.get_json()
        title = body.get('title',None)
        releaseDate = body.get('releaseDate',None)
        
        if title:
            movie.title = title
        if releaseDate:
            movie.releaseDate = releaseDate
		
        try:
            movie.update()

        except Exception:
	        raise InternalServerError

        return jsonify({
        'status': 'Success',
        'movie': movie.format() 
    	})

	# error handlers 
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
    
    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        return response

    return app


APP = create_app()

if __name__ == '__main__':
    APP.run()
