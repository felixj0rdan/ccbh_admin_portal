from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
import random
import requests
import datetime
from random import randrange

from models.users import UserModel
from models.appointments import AppointmentModel

from flask import request, jsonify, send_file, send_from_directory, url_for, redirect, render_template
from werkzeug.utils import secure_filename
import os
import re
import json

from flask_jwt_extended import create_access_token, create_refresh_token, jwt_refresh_token_required, get_jwt_identity, jwt_required, get_raw_jwt

from blacklist import BLACKLIST

from itsdangerous import URLSafeTimedSerializer, SignatureExpired


class UserRegister(Resource):

    def post(self):
        _user_parser = reqparse.RequestParser()

        _user_parser.add_argument('name',
                                  type=str,
                                  required=True,
                                  help="This field cannot be blank."
                                  )
        _user_parser.add_argument('phonenumber',
                                  type=str,
                                  required=True,
                                  help="This field cannot be blank."
                                  )
        _user_parser.add_argument('email',
                                  type=str,
                                  required=True,
                                  help="This field cannot be blank."
                                  )
        _user_parser.add_argument('password',
                                  type=str,
                                  required=True,
                                  help="This field cannot be blank."
                                  )

        data = _user_parser.parse_args()
        # print(data['phonenumber'])
        if UserModel.find_by_phonenumber(data['phonenumber']):
            return {"message": "A user with that phone already exists"}, 400
        elif UserModel.find_by_email(data['email']):
            return {"message": "A user with that email already exists"}, 400
        else:

            user = UserModel(data['email'], data['phonenumber'], data['name'])
            user.password = data['password']
            user.save_to_db()

            return {"message": "User created successfully."}, 200


class UserLogin(Resource):
    def post(self):
        _user_parser = reqparse.RequestParser()
        _user_parser.add_argument('phonenumber',
                                  type=str,
                                  required=True,
                                  help="This field cannot be blank."
                                  )
        _user_parser.add_argument('password',
                                  type=str,
                                  required=True,
                                  help="This field cannot be blank."
                                  )
        data = _user_parser.parse_args()

        user = UserModel.find_by_phonenumber(data['phonenumber'])
        if user:
            if safe_str_cmp(user.password, data['password']):
                if(user.status == 2):
                    access_token = create_access_token(
                        identity=user.id, fresh=True)
                    refresh_token = create_refresh_token(user.id)
                    return {
                        'access_token': access_token,
                        'refresh_token': refresh_token,
                        'user_id': user.id,
                        "email": user.email
                    }, 200
                elif(user.status == 3):
                    access_token = create_access_token(
                        identity=user.id, fresh=True)
                    refresh_token = create_refresh_token(user.id)
                    return {
                        'access_token': access_token,
                        'refresh_token': refresh_token,
                        'user_id': user.id,
                        "email": user.email
                    }, 200
                elif(user.status == 1):
                    # token = s.dumps(user.email, salt='email-confirm')

                    # user.save_to_db()
                    # print(user.id)
                    # user.send_verification_email(user.email, token)

                    return{"message": "Account not verified", "status": user.status, "id": user.id}, 401
            return {"message": "Invalid Credentials!"}, 401
        return {"message": "User not found!", "status": 0}, 404


class UserAppoinments(Resource):

    @jwt_required
    def get(self):

        try:
            user_id = get_jwt_identity()

            appoinments = [appointment.json()
                           for appointment in AppointmentModel.find_by_user(user_id)]

            return {'Appointments': appoinments, 'Message': 'Ok'}

        except:

            return{'Message': 'Error'}


class UserAppoinments2(Resource):

    @jwt_required
    def get(self, user_id):

        try:
            appoinments = [appointment.json()
                           for appointment in AppointmentModel.find_by_user(user_id)]

            return {'Appointments': appoinments, 'Message': 'Ok'}

        except:

            return{'Message': 'Error'}
