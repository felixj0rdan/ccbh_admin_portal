from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
import random
import requests
import datetime
from flask import request, jsonify, send_file, send_from_directory, url_for, redirect
from werkzeug.utils import secure_filename

import os
import re
import json

from models.appointments import AppointmentModel
from models.users import UserModel

from flask_jwt_extended import create_access_token, create_refresh_token, jwt_refresh_token_required, get_jwt_identity, jwt_required, get_raw_jwt

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'docx', 'doc', 'pdf'])

UPLOAD_FOLDER = 'documents'


class newAppointment(Resource):

    @jwt_required
    def post(self):
        _user_parser = reqparse.RequestParser()

        _user_parser.add_argument('summary',
                                  type=str,
                                  required=True,
                                  help="This field cannot be blank."
                                  )
        _user_parser.add_argument('doc',
                                  type=str,
                                  required=True,
                                  help="This field cannot be blank."
                                  )

        data = _user_parser.parse_args()
        try:
            user_id = get_jwt_identity()

            user = UserModel.find_by_id(user_id)

            data['user_name'] = user.name
            data['user_id'] = user_id

            appointment = AppointmentModel(**data)
            appointment.save_to_db()

            return {'Message': 'Ok'}
        except:
            return {'Message': 'Error'}


class UploadDoc(Resource):

    @jwt_required
    def post(self):

        # print(request.files)
        if 'file' not in request.files:
            return {'message': 'No file uploaded!'}, 400

        files = request.files.getlist('file')
        errors = {}
        success = False
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)
        for file in files:
            if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:

                # if user.doc != "":
                #     print(UPLOAD_FOLDER + "/" + user.doc.split('/')[-1])
                #     try:
                #         os.remove(UPLOAD_FOLDER + "/" +
                #                   user.doc.split('/')[-1])
                #     except:
                #         pass
                #     user.doc = ""
                #     user.save_to_db()

                ext = secure_filename(file.filename).rsplit('.', 1)[1].lower()
                filename = secure_filename(file.filename)

                URL = request.url_root[:-1]
                print(True)
                print(URL)
                doc_name = "doc" + str(user.doc_count)
                user.doc_count = user.doc_count + 1
                doc = doc_name + filename

                file.save(os.path.join(UPLOAD_FOLDER, doc))

                # user.doc = URL + "/appointment-doc/" + doc
                doc_link = URL + "/appointment-doc/" + doc
                user.save_to_db()
                success = True

            else:
                errors[file.filename] = 'File type is not allowed'

        if success and errors:
            errors['message'] = 'File(s) successfully uploaded'
            resp = jsonify(errors)
            resp.status_code = 500
            return resp
        if success:
            resp = jsonify({'message': 'Files successfully uploaded'})
            resp.status_code = 201
            return {'message': "Success", "doc": doc_link}
        else:
            resp = jsonify(errors)
            resp.status_code = 500
            return resp


class getDoc(Resource):

    @jwt_required
    def get(self, path):
        print(path)
        try:
            return send_from_directory(UPLOAD_FOLDER, path=path)
        except FileNotFoundError:
            return {'message': 'Doc not Found'}, 404
