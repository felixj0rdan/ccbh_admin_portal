from db import db
import datetime
import requests
from flask import Flask, request, url_for


class AppointmentModel(db.Model):

    __tablename__ = "appointments"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer())
    user_name = db.Column(db.String())
    summary = db.Column(db.String())
    doc = db.Column(db.String())
    datetime = db.Column(db.String(), default=datetime.datetime.now())

    def __init__(self, user_id, user_name, summary, doc):

        self.user_id = user_id
        self.user_name = user_name
        self.summary = summary
        self.doc = doc

    def json(self):

        return {
            "DateTime": self.datetime,
            "Summary": self.summary,
            "Doc": self.doc,
            "UserId": self.user_id
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_by_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id)

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
