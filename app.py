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

jwt = JWTManager(app)

api.add_resource(UserRegister, '/register')

if __name__ == '__main__':
    db.init_app(app)
    app.run(port=5000, debug=True)
