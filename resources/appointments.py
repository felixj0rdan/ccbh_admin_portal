from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
import random
import requests
import datetime
from flask import request, jsonify, send_file, send_from_directory, url_for, redirect
from werkzeug.utils import secure_filename
from werkzeug.datastructures import ImmutableMultiDict

import os
import re
import json

from models.appointments import AppointmentModel
from models.users import UserModel

from flask_jwt_extended import create_access_token, create_refresh_token, jwt_refresh_token_required, get_jwt_identity, jwt_required, get_raw_jwt

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'docx', 'doc', 'pdf' ])

UPLOAD_FOLDER = 'documents'


class newAppointment(Resource):

    # @jwt_required
    def post(self):

        data = dict(request.form)
        print(data)

        try:
            if not data['summary']:
                return {'Message': 'Summary can not be blank.'}
        except:
            return {'Message': 'Summary can not be blank.'}

        if 'file' not in request.files:
            print("no file")
            return {'message': 'No file uploaded!'}, 400

        files = request.files.getlist('file')

        for file in files:
            if not (file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
                return {'Message': 'File type not allowed'}

        try:
            # user_id = get_jwt_identity()
            user_id = 2

            user = UserModel.find_by_id(user_id)

            data['user_name'] = user.name
            data['user_id'] = user_id
            data['doc'] = None

            appointment = AppointmentModel(**data)
            appointment.save_to_db()

            print(appointment.id)

            for file in files:
                if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:

                    ext = secure_filename(file.filename).rsplit('.', 1)[
                        1].lower()
                    filename = secure_filename(file.filename)

                    URL = request.url_root[:-1]
                    doc = 'user' + str(user_id) + 'appointment' + \
                        str(appointment.id) + filename

                    file.save(os.path.join(UPLOAD_FOLDER, doc))

                    doc_link = URL + "/appointment-doc/" + doc
                    appointment.doc = doc_link
                    appointment.save_to_db()

                else:
                    return {'Message': '{} file type not allowed.'.format(file.filename)}

            return {'Message': 'Ok'}

        except:
            return {'Message': 'Error'}


class getDoc(Resource):

    @jwt_required
    def get(self, path):
        print(path)
        try:
            return send_from_directory(UPLOAD_FOLDER, path=path)
        except FileNotFoundError:
            return {'Message': 'Doc not Found'}, 404


class getAppointments(Resource):

    def get(self):
        try:
            appointments = [appointment.json() for appointment in AppointmentModel.find_all()]
            return {'Appointments': appointments, 'Message': 'Ok'}, 200
        except:
            return {'Message': 'Error'}