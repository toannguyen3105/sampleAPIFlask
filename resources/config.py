from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from models.config import ConfigModel
from models.user import UserModel

from utils.date_format import getTimeStamp

ADMINISTRATOR_TITLE = "Administrator"


class ConfigRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("title",
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument("description",
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    @jwt_required()
    def post(self):
        claims = get_jwt()
        if not claims["is_admin"]:
            return {"message": "Admin privilege required."}, 401

        data = self.parser.parse_args()

        title = data["title"]
        description = data["description"]

        if ConfigModel.find_by_name(title):
            return {"message": "Cấu hình với tên '{}' đã tồn tại.".format(title)}, 400
        else:
            item = ConfigModel(title, description, 1, getTimeStamp(), ADMINISTRATOR_TITLE, None, None)
            item.save_to_db()

            return {"message": "Thêm cấu hình '{}' thành công.".format(title)}, 201


class Config(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("title",
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument("description",
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument("status",
                        type=int,
                        required=False,
                        )

    @jwt_required()
    def get(self, config_id: int):
        claims = get_jwt()
        if not claims["is_admin"]:
            return {"message": "Admin privilege required."}, 401

        item = ConfigModel.find_by_id(config_id)
        if not item:
            return {
                       "status": 404,
                       "message": "Not found",
                       "data": None
                   }, 404

        return {
                   "status": 200,
                   "message": "Get info success",
                   "data": item.json()
               }, 200

    @jwt_required()
    def delete(self, config_id: int):
        claims = get_jwt()
        if not claims["is_admin"]:
            return {"message": "Admin privilege required."}, 401

        item = ConfigModel.find_by_id(config_id)
        if item:
            item.delete_from_db()
            return {
                       "status": 200,
                       "message": "Xóa item thành công.",
                       "data": None
                   }, 200

        return {
                   "status": 404,
                   "message": "Không tìm thấy item.",
                   "data": None
               }, 404

    @jwt_required()
    def put(self, config_id: int):
        claims = get_jwt()
        if not claims["is_admin"]:
            return {"message": "Admin privilege required."}, 401

        item = ConfigModel.find_by_id(config_id)
        if item is None:
            return {
                       "status": 404,
                       "message": "Config với id '{}' is not existed.".format(config_id),
                       "data": None
                   }, 404

        data = self.parser.parse_args()
        title = data["title"]
        description = data["description"]
        status = data["status"]

        item.title = title
        item.description = description
        item.status = status
        item.updated_at = getTimeStamp()
        item.updated_by = ADMINISTRATOR_TITLE

        item.save_to_db()

        # Save log
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)

        return {
                   "message": "Thành công",
                   "data": item.json()
               }, 200


class ConfigList(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        if not claims["is_admin"]:
            return {"message": "Admin privilege required."}, 401

        user_id = get_jwt_identity()
        items = [item.json() for item in ConfigModel.find_all()]

        if user_id:
            return {
                       "message": "Danh sách item thành công",
                       "data": [item for item in items],
                       "total": len(ConfigModel.find_all())
                   }, 200


class ConfigBannerList(Resource):
    def get(self):
        items = [item.json() for item in ConfigModel.find_all_banner()]

        return {
                   "message": "Danh sách item thành công",
                   "data": [item for item in items],
                   "total": len(ConfigModel.find_all())
               }, 200


class ConfigRateItem(Resource):
    def get(self):
        item_model = ConfigModel.find_by_name("RATE")
        item = item_model.json()
        return {
                   "message": "Success",
                   "data": item
               }, 200
