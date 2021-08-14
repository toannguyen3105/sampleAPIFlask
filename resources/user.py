import os

import requests
import json
from datetime import timedelta

from decouple import config
from werkzeug.datastructures import FileStorage
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt, get_jwt_identity

from models.user import UserModel
from models.config import ConfigModel

from utils.date_format import getTimeStamp
from utils.proxy import getCurrentIpUser

CSGO_EMPIRE_URL = config("CSGO_EMPIRE_URL")
CONTENT_TYPE = "application/json"
ADMINISTRATOR_TITLE = "Administrator"
UPLOAD_IMAGE_DIR = config("UPLOAD_IMAGE_DIR")
UPLOAD_IMAGE_PATH = config("UPLOAD_IMAGE_PATH")


class UserSteam(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("amount",
                        type=int,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument("steam_id",
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    def post(self):
        data = self.parser.parse_args()

        amount = data["amount"]
        steam_id = data["steam_id"]

        # Pretip
        config_cookie = ConfigModel.find_by_name("COOKIE")
        saved_cookie = config_cookie.description

        headers = {
            "cookie": saved_cookie,
            "Content-Type": CONTENT_TYPE
        }

        payload = {
            "steam_id": steam_id,
            "amount": amount
        }

        res = requests.post("{}api/v2/user/chat/pretip".format(CSGO_EMPIRE_URL), data=json.dumps(payload),
                            headers=headers)
        if res.status_code == 200:
            return {
                "message": "Get info success",
                "data": res.json()
            }

        return {
            "message": "Get info have error",
            "data": {}

        }


class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("username",
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    parser.add_argument("password",
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    parser.add_argument("steam_id",
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    parser.add_argument("phone",
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    def post(self):
        data = self.parser.parse_args()

        username = data["username"]
        steam_id = data["steam_id"]
        phone = data["phone"]
        if UserModel.find_by_username(username):
            return {"message": "Tài khoản với tên '{}' đã tồn tại.".format(username)}, 400
        else:
            user = UserModel(username, generate_password_hash(data["password"]), 0, steam_id, None, None,
                             getCurrentIpUser(), 1, None, None, None, None, phone, None, None, getTimeStamp(), None,
                             None, None)
            user.save_to_db()

            return {"message": "Đăng ký tài khoản '{}' thành công.".format(username)}, 201


class UserUpload(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("file",
                        type=FileStorage,
                        required=True,
                        help="This field cannot be blank.",
                        location='files',
                        )

    @jwt_required()
    def post(self):
        def allowed_file(filename):
            ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        data = self.parser.parse_args()

        file = data.get("file")
        if file.filename == '':
            return {
                       "status": 400,
                       "message": "No file selected for uploading",
                       "data": None
                   }, 400
        if file and allowed_file(file.filename):
            filename = str(getTimeStamp()) + "_" + secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_IMAGE_DIR, filename)
            file.save(save_path)

            return {
                       "status": 201,
                       "message": "File successfully uploaded",
                       "data": UPLOAD_IMAGE_PATH + filename
                   }, 201

        else:
            return {
                "status": 400,
                "message": "Allowed file types are txt, pdf, png, jpg, jpeg, gif",
                "data": None
            }


class UserLogin(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("username",
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument("password",
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    def post(self):
        data = self.parser.parse_args()
        user = UserModel.find_by_username(data["username"])
        if user and check_password_hash(user.password, data["password"]):
            expires = timedelta(days=7)
            access_token = create_access_token(identity=user.id, expires_delta=expires, fresh=True)
            refresh_token = create_refresh_token(user.id)

            return {
                       "access_token": access_token,
                       "refresh_token": refresh_token
                   }, 200
        else:
            return {
                       "message": "Sai thông tin đăng nhập."
                   }, 401


class UserAddBalance(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("balance",
                        type=int,
                        required=True,
                        help="This field cannot be blank."
                        )

    @jwt_required()
    def put(self, user_id: int):
        claims = get_jwt()
        if not claims["is_admin"]:
            return {"message": "Admin privilege required."}, 401

        user = UserModel.find_by_id(user_id)
        if user is None:
            return {"message": "User with id '{}' is not existed.".format(user_id)}, 404

        data = self.parser.parse_args()
        balance = data["balance"]
        user.balance = user.balance + balance
        user.updated_at = getTimeStamp()
        user.updated_by = ADMINISTRATOR_TITLE

        user.save_to_db()

        return {
                   "message": "Updated successful",
                   "data": user.json()
               }, 200


class User(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("firstName",
                        type=str,
                        required=False,
                        )
    parser.add_argument("lastName",
                        type=str,
                        required=False,
                        )
    parser.add_argument("balance",
                        type=int,
                        required=False,
                        )
    parser.add_argument("email",
                        type=str,
                        required=False,
                        )
    parser.add_argument("avatar",
                        type=str,
                        required=False,
                        )
    parser.add_argument("phone",
                        type=str,
                        required=False,
                        )
    parser.add_argument("steamId",
                        type=str,
                        required=False,
                        )
    parser.add_argument("status",
                        type=int,
                        required=False,
                        )

    @jwt_required()
    def get(self, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {
                       "status": 404,
                       "message": "Not found",
                       "data": None
                   }, 404

        return {
                   "status": 200,
                   "message": "Success",
                   "data": user.json()
               }, 200

    @jwt_required()
    def delete(self, user_id: int):
        claims = get_jwt()
        if not claims["is_admin"]:
            return {
                       "status": 401,
                       "message": "Admin privilege required.",
                       "data": None
                   }, 401

        user = UserModel.find_by_id(user_id)
        if user:
            user.delete_from_db()
            return {
                       "status": 200,
                       "message": "Delete successful",
                       "data": None
                   }, 200
        else:
            return {
                       "status": 404,
                       "message": "User is not found",
                       "data": None
                   }, 404

    @jwt_required()
    def put(self, user_id: int):
        claims = get_jwt()
        if not claims["is_admin"]:
            return {"message": "Admin privilege required."}, 401

        user = UserModel.find_by_id(user_id)
        if user is None:
            return {
                       "status": 404,
                       "message": "User with id '{}' is not existed.".format(user_id),
                       "data": None
                   }, 404

        data = self.parser.parse_args()
        status = data["status"]
        first_name = data["firstName"]
        last_name = data["lastName"]
        balance = data["balance"]
        email = data["email"]
        phone = data["phone"]
        steam_id = data["steamId"]
        avatar = data["avatar"]

        user.firstname = first_name
        user.lastname = last_name
        user.balance = balance
        user.email = email
        user.phone = phone
        user.avatar = avatar
        user.steam_id = steam_id
        user.status = status
        user.updated_at = getTimeStamp()
        user.updated_by = ADMINISTRATOR_TITLE

        user.save_to_db()

        return {
                   "status": 200,
                   "message": "Updated successful",
                   "data": user.json()
               }, 200


class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200


class UserProfile(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)
        return {
                   "status": "200",
                   "message": "Success",
                   "data": user.json()
               }, 200


class UserList(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        if not claims["is_admin"]:
            return {"message": "Admin privilege required."}, 401

        user_id = get_jwt_identity()

        users = [user.json() for user in UserModel.find_all()]
        if user_id:
            return {
                       "status": 200,
                       "message": "Danh sách user thành công",
                       "data": [user for user in users],
                       "total": len(UserModel.find_all())
                   }, 200
        else:
            return {
                       "status": 200,
                       "message": "More data available if you log in.",
                       "data": [user["username"] for user in users],
                       "total": len(UserModel.find_all())
                   }, 200
