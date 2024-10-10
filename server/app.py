#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    response = [
        {
            'id': hero.id,
            'name': hero.name,
            'super_name': hero.super_name
        } for hero in heroes
    ]
    return jsonify(response)

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = Hero.query.get(id)
    if hero is None:
        return jsonify({'error': 'Hero not found'}), 404
    return jsonify(hero.to_dict())

@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    return jsonify([power.to_dict() for power in powers])

@app.route('/powers/<int:id>', methods=['GET'])
def get_power(id):
    power = Power.query.get(id)
    if power is None:
        return jsonify({'error': 'Power not found'}), 404
    return jsonify(power.to_dict())

@app.route('/powers/<int:power_id>', methods=['PATCH'])
def update_power(power_id):
    power = Power.query.get(power_id)
    if not power:
        return jsonify({'error': 'Power not found'}), 404
    
    data = request.json
    if 'description' in data:
        if len(data['description']) < 20:
            return jsonify({'errors': ["validation errors"]}), 400
        
        power.description = data['description']
        db.session.commit()
        return jsonify(power.to_dict())
    
    return jsonify({'errors': ["No valid fields to update"]}), 400
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.json

    if 'strength' not in data or data['strength'] not in ['Strong', 'Weak', 'Average']:
        return jsonify({'errors': ["validation errors"]}), 400

    if 'hero_id' not in data or 'power_id' not in data:
        return jsonify({'errors': ["Hero ID and Power ID are required"]}), 400

    hero = Hero.query.get(data['hero_id'])
    if hero is None:
        return jsonify({'errors': ["Hero not found"]}), 404

    power = Power.query.get(data['power_id'])
    if power is None:
        return jsonify({'errors': ["Power not found"]}), 404

    try:
        new_hero_power = HeroPower(
            strength=data['strength'],
            hero=hero,
            power=power
        )
        db.session.add(new_hero_power)
        db.session.commit()
        return jsonify(new_hero_power.to_dict()), 201  
    except ValueError as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': ["Failed to create HeroPower"]}), 400


if __name__ == '__main__':
    app.run(port=5555, debug=True)
