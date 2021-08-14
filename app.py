import os

from flask import Flask, jsonify
from flask_cors import CORS
from flask_restful import Api
from flask_jwt_extended import JWTManager

from db import db
from resources.user import UserRegister, UserLogin, User, UserList, TokenRefresh, UserSteam, UserAddBalance, \
    UserProfile, UserUpload
from resources.log import LogList
from resources.item import ItemList, Item, ItemRegister
from resources.config import ConfigList, Config, ConfigRegister, ConfigBannerList, ConfigRateItem
from resources.transaction import Transaction, TransactionList

__author__ = "@toannguyen3105"

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_SECRET_KEY'] = '_____***!3Em123pire224h1!***_____'
api = Api(app)

# Handle upload file
app.config['UPLOAD_FOLDER'] = 'C:\\Users\\nguye\\Downloads\\Documents\\uploads\\images'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024


@app.before_first_request
def create_tables():
    db.create_all()


jwt = JWTManager(app)


@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:
        return {'is_admin': True}
    return {'is_admin': False}


@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'description': 'The token is expired.',
        'error': 'token_expired'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'description': 'The token is invalid.',
        'error': 'invalid_token'
    }), 401


@jwt.unauthorized_loader
def mission_token_callback(error):
    return jsonify({
        'description': 'The token is required.',
        'error': 'invalid_token'
    }), 401


@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        'description': 'The token is not fresh.',
        'error': 'fresh_token_required'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        'description': 'The token has been revoked.',
        'error': 'token_revoked'
    }), 401


api.add_resource(UserSteam, '/steam')
api.add_resource(UserAddBalance, '/addBalance/<int:user_id>')
api.add_resource(UserUpload, '/upload')
api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserList, '/users')
api.add_resource(UserProfile, '/profile')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(LogList, '/logs')
api.add_resource(ItemList, '/items')
api.add_resource(ItemRegister, '/item')
api.add_resource(Item, '/item/<int:item_id>')
api.add_resource(ConfigList, '/configs')
api.add_resource(ConfigRegister, '/config')
api.add_resource(Config, '/config/<int:config_id>')
api.add_resource(ConfigBannerList, '/banners')
api.add_resource(ConfigRateItem, '/rate')
api.add_resource(Transaction, '/transaction')
api.add_resource(TransactionList, '/transactions')

if __name__ == '__main__':
    db.init_app(app)
    app.run(port=5000, debug=True)
