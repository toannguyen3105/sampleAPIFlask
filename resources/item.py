import requests
import json
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from decouple import config

from models.item import ItemModel
from models.user import UserModel
from models.config import ConfigModel

from utils.date_format import getTimeStamp
from utils.telegram.send_message import send_message_telegram

ADMINISTRATOR_TITLE = "Administrator"
CSGO_EMPIRE_URL = config("CSGO_EMPIRE_URL")
UUID = "096bc79d-96ce-432e-9c7a-97195f50dffe"
CONTENT_TYPE = "application/json"


class ItemRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("amount",
                        type=float,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument("steamId",
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    @jwt_required()
    def post(self):
        data = self.parser.parse_args()
        amount = data["amount"]
        steam_id = data["steamId"]

        if amount < 0:
            return {
                       "message": "Số lượng coin {} ít nhất là 1".format(amount),
                       "status": 400
                   }, 400

        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)
        rate_config = ConfigModel.find_by_name("RATE")
        rate = int(rate_config.description)
        if user.balance < amount * rate:
            return {
                       "message": "Số dư tài khoản {} không đủ để thanh toán".format(user.username),
                       "status": 400
                   }, 400

        # Step 1: Security token
        config_cookie = ConfigModel.find_by_name("COOKIE")
        saved_cookie = config_cookie.description

        headers = {
            "cookie": saved_cookie,
            "Content-Type": CONTENT_TYPE
        }

        two_fa_code_config = ConfigModel.find_by_name("2FA")
        saved_two_fa_code = two_fa_code_config.description

        payload = {
            "code": saved_two_fa_code,
            "uuid": UUID,
            "type": "onetime",
            "remember_device": False
        }
        res = requests.post("{}api/v2/user/security/token"
                            .format(CSGO_EMPIRE_URL), data=json.dumps(payload), headers=headers)

        message = ""
        if res.status_code == 200:
            # Step 2: Tip user
            payload = {
                "steam_id": steam_id,
                "amount": amount * 100,
                "onetime_token": res.json()["token"]
            }

            res = requests.post("{}api/v2/user/chat/tip".format(CSGO_EMPIRE_URL), data=json.dumps(payload),
                                headers=headers)
            if res.status_code == 200:
                res = requests.get("{}api/v2/metadata".format(CSGO_EMPIRE_URL), headers=headers)
                res_json = res.json()
                balance = res_json["user"]["balance"]
                message += "Account {} was transfer success {} coin to ({}). CsgoEmpire's balance: {}".format(
                    user.username, amount, steam_id, balance
                )

                # Update accounts balance
                user.balance = user.balance - amount * rate
                user.updated_at = getTimeStamp()
                user.updated_by = ADMINISTRATOR_TITLE
                user.save_to_db()

                # Add item
                item = ItemModel(amount, steam_id, user_id, 1, getTimeStamp(), ADMINISTRATOR_TITLE, None, None)
                item.save_to_db()

                # Send a message to telegram
                send_message_telegram(message)

                return {
                           "message": "Giao dịch thành công {} coin".format(amount),
                           "status": 201,
                       }, 201

        message += "Account {} with a transaction of {} coin to ({}) has an error '{}'".format(
            user.username, amount, steam_id,
            res.json()["message"] if "message" in res.json() else "Something went wrong"
        )

        # Add item
        item = ItemModel(amount, steam_id, user_id, 0, getTimeStamp(), ADMINISTRATOR_TITLE, None, None)
        item.save_to_db()

        # Send a message to telegram
        send_message_telegram(message)
        return {
                   "message": "Tài khoản {} giao dịch {} coin với SteamID ({}) xảy ra lỗi '{}'. Vui lòng thử lại sau 30s".format(
                       user.username, amount, steam_id,
                       res.json()["message"] if "message" in res.json() else "Something went wrong"),
                   "status": 500
               }, 500


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("status",
                        type=int,
                        required=True,
                        help="This field cannot be blank."
                        )

    @jwt_required()
    def get(self, item_id: int):
        item = ItemModel.find_by_id(item_id)
        if not item:
            return {"message": "Item not found."}, 404

        return item.json(), 200

    @jwt_required()
    def delete(self, item_id: int):
        claims = get_jwt()
        if not claims["is_admin"]:
            return {"message": "Admin privilege required."}, 401

        item = ItemModel.find_by_id(item_id)
        if item:
            item.delete_from_db()
            return {"message": "Deleted successfully."}, 200

        return {"message": "Item not found."}, 404

    @jwt_required()
    def put(self, item_id: int):
        item = ItemModel.find_by_id(item_id)
        if item is None:
            return {"message": "Item with id '{}' is not existed.".format(item_id)}, 404

        data = self.parser.parse_args()
        status = data["status"]
        item.status = status
        item.updated_at = getTimeStamp()
        item.updated_by = ADMINISTRATOR_TITLE

        item.save_to_db()

        return {
                   "message": "Updated successful",
                   "data": item.json()
               }, 200


class ItemList(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        if not claims["is_admin"]:
            return {"message": "Admin privilege required."}, 401

        items = [item.json_list(user) for item, user in ItemModel.find_all_join()]
        user_id = get_jwt_identity()
        if user_id:
            return {
                       "message": "List item",
                       "data": items,
                       "total": len(ItemModel.find_all())
                   }, 200
