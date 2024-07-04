#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/campers', methods=['GET', 'POST'])
def get_campers():
    if request.method == "GET":
        list_of_campers = Camper.query.all()
        campers_dict = [camper.to_dict() for camper in list_of_campers]
        return make_response(jsonify(campers_dict), 200)
    
    if request.method == "POST":
        data = request.get_json()
        name = data.get('name')
        age = data.get('age')

        try:
            new_camper = Camper(name=name, age=age)
            db.session.add(new_camper)
            db.session.commit()
            return make_response(jsonify(new_camper.to_dict()), 201)
        except ValueError as e:
            db.session.rollback()
            return make_response(jsonify({"errors": str(e)}), 400)

@app.route('/campers/<int:id>', methods=['GET', 'PATCH'])
def get_campler_by_id(id):
    camper = Camper.query.filter_by(id=id).first()
    
    if camper:
        if request.method == "GET":
            camper_dict = camper.to_dict(rules=('-signups.camper', 'signups'))
            return make_response(jsonify(camper_dict), 200)

        if request.method == "PATCH":
            data = request.get_json()
            errors = []

            try:
                if 'name' in data:
                    camper.name = data['name']
                if 'age' in data:
                    camper.age = data['age']
                
                db.session.commit()
                camper_dict = camper.to_dict(rules=('-signups.camper', 'signups'))
                return make_response(jsonify(camper_dict), 202)
            except ValueError as e:
                db.session.rollback()
                errors.append(str(e))
                return make_response(jsonify({"errors": errors}), 400)
            except Exception as e:
                db.session.rollback()
                return make_response(jsonify({"errors": [str(e)]}), 500)
    else:
        return jsonify({"error": "Camper not found"}), 404

@app.route('/activities', methods=['GET'])
def get_activities():
    if request.method == 'GET':
        list_of_activities = Activity.query.all()
        activities_dict = [activity.to_dict() for activity in list_of_activities]
        return make_response(jsonify(activities_dict), 200)

@app.route('/activities/<int:id>', methods=['GET', 'DELETE'])
def delete_activity_by_id(id):

    activity = Activity.query.filter_by(id=id).first()

    if request.method == 'GET':
        try:
            return make_response(jsonify(activity.to_dict()), 200)
        except ValueError as e:
            return make_response(jsonify({"error": str(e)}), 404)

    if request.method == 'DELETE':

        if activity:
            try:
                db.session.delete(activity)
                db.session.commit()
                return make_response(jsonify({"message": "success"}), 204)
            except ValueError as e:
                return make_response(jsonify({"errors": str(e)}), 400)
        return make_response(jsonify({'error': 'Activity not found'}), 404)


@app.route("/signups", methods=['POST'])
def create_signup():

    if request.method == 'POST':
        data = request.get_json()
        time = data.get('time')
        camper_id = data.get('camper_id')
        activity_id = data.get('activity_id')

        try:
            new_signup = Signup(
                time=time,
                camper_id=camper_id,
                activity_id=activity_id
            )
            db.session.add(new_signup)
            db.session.commit()
            return make_response(jsonify(new_signup.to_dict()), 201)
        except ValueError as e:
            db.session.rollback()
            return make_response(jsonify({"errors": [str(e)]}), 400)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"errors": [str(e)]}), 500)



if __name__ == '__main__':
    app.run(port=5555, debug=True)
