import flask
from flask import jsonify
from . import db_session
from .users import User
import functions

blueprint = flask.Blueprint(
    'user_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify(
        {
            'users':
                [item.to_dict(only=('surname',
                                    'name',
                                    'age',
                                    'position',
                                    'speciality',
                                    'address',
                                    'city_from',
                                    'email'))
                 for item in users]
        }
    )


@blueprint.route('/api/users/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    db_sess = db_session.create_session()
    users = db_sess.query(User).get(user_id)
    if not users:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'users': users.to_dict(only=('surname',
                                         'name',
                                         'age',
                                         'position',
                                         'speciality',
                                         'address',
                                         'city_from',
                                         'email'))
        }
    )


@blueprint.route('/api/users', methods=['POST'])
def create_user():
    if not flask.request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in flask.request.json for key in
                 ['surname',
                  'name',
                  'age',
                  'position',
                  'speciality',
                  'address',
                  'email',
                  'city_from',
                  'hashed_password']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    print(1)
    user = User(
        surname=flask.request.json['surname'],
        name=flask.request.json['name'],
        age=flask.request.json['age'],
        position=flask.request.json['position'],
        speciality=flask.request.json['speciality'],
        address=flask.request.json['address'],
        email=flask.request.json['email'],
        city_from=flask.request.json['city_from'],
        hashed_password=flask.request.json['hashed_password']
    )
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    db_sess.delete(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:user_id>', methods=['PUT'])
def put_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    if not user:
        return jsonify({'error': 'Not found'})
    elif not all(key in flask.request.json for key in
                 ['surname',
                  'name',
                  'age',
                  'position',
                  'speciality',
                  'address',
                  'email']):
        return jsonify({'error': 'Bad request'})
    user.surname = flask.request.json['surname']
    user.name = flask.request.json['name']
    user.age = flask.request.json['age']
    user.position = flask.request.json['position']
    user.speciality = flask.request.json['speciality']
    user.address = flask.request.json['address']
    user.email = flask.request.json['email']
    db_sess.commit()
    return jsonify(
        {
            'jobs': user.to_dict(only=('surname',
                                       'name',
                                       'age',
                                       'position',
                                       'speciality',
                                       'address',
                                       'email'))
        }
    )


@blueprint.route('/api/users_show/<int:user_id>', methods=['GET'])
def get_image_user(user_id):
    db_sess = db_session.create_session()
    users = db_sess.query(User).get(user_id)
    if not users:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'users_id': user_id,
            'image': functions.geocoder(users.city_from)
        }
    )
