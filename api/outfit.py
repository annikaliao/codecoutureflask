import json
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource # used for REST API building
from datetime import datetime
from werkzeug.utils import secure_filename
import os

from model.outfits import Outfit

outfit_api = Blueprint('outfit_api', __name__,
                   url_prefix='/api/outfits')

# API docs https://flask-restful.readthedocs.io/en/latest/api.html
api = Api(outfit_api)

#UPLOAD_FOLDER = '/path/to/upload/folder'

#ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Set the upload folder
#outfit_api.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


class OutfitAPI:        
    class _CRUD(Resource):  # outfit API operation for Create, Read.  THe Update, Delete methods need to be implemeented
        def post(self): # Create method
            ''' Read data for json body '''
            body = request.get_json()
            
            ''' Avoid garbage in, error checking '''
            # validate name
            name = body.get('name')
            if name is None or len(name) < 2:
                return {'message': f'Name is missing, or is less than 2 characters'}, 400
            # validate uid
            uid = body.get('uid')
            if uid is None or len(uid) < 2:
                return {'message': f'User ID is missing, or is less than 2 characters'}, 400
            # look for password and dob
            password = body.get('password')
            dob = body.get('dob')

            ''' #1: Key code block, setup USER OBJECT '''
            uo = Outfit(name=name, 
                      uid=uid)
            
            ''' Additional garbage error checking '''
            # set password if provided
            if password is not None:
                uo.set_password(password)
            # convert to date type
            if dob is not None:
                try:
                    uo.dob = datetime.strptime(dob, '%Y-%m-%d').date()
                except:
                    return {'message': f'Date of birth format error {dob}, must be mm-dd-yyyy'}, 400
            
            ''' #2: Key Code block to add user to database '''
            # create user in database
            outfit = uo.create()
            # success returns json of user
            if outfit:
                return jsonify(outfit.read())
            # failure returns error
            return {'message': f'Processed {name}, either a format error or User ID {uid} is duplicate'}, 400

        def get(self): # Read Method
            outfits = Outfit.query.all()    # read/extract all outfits from database
            json_ready = [outfit.read() for outfit in outfits]  # prepare output in json
            return jsonify(json_ready)  # jsonify creates Flask response object, more specific to APIs than json.dumps
    
    class _Security(Resource):

        def post(self):
            ''' Read data for json body '''
            body = request.get_json()
            
            ''' Get Data '''
            uid = body.get('uid')
            if uid is None or len(uid) < 2:
                return {'message': f'User ID is missing, or is less than 2 characters'}, 400
            password = body.get('password')
            
            ''' Find user '''
            outfit = Outfit.query.filter_by(_uid=uid).first()
            if outfit is None or not outfit.is_password(password):
                return {'message': f"Invalid user id or password"}, 400
            
            ''' authenticated user '''
            return jsonify(outfit.read())

            

    # building RESTapi endpoint
    api.add_resource(_CRUD, '/')
    api.add_resource(_Security, '/authenticate')
    