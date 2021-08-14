from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from flask_restful import Resource, reqparse

from models.transaction import TransactionModel
from models.user import UserModel
from utils.date_format import getTimeStamp

transaction_type = 'emp'

_transaction_parser = reqparse.RequestParser()
_transaction_list_parser = reqparse.RequestParser()

# LIST CONFIGURATION: REQUEST PARSER
_transaction_list_parser.add_argument('page',
                                      type=int,
                                      required=False,
                                      help="This field cannot be blank."
                                      )
_transaction_list_parser.add_argument('page_size',
                                      type=int,
                                      required=False,
                                      help="This field cannot be blank."
                                      )
_transaction_list_parser.add_argument('filters',
                                      type=str,
                                      required=False,
                                      help="This field cannot be blank."
                                      )
_transaction_list_parser.add_argument('order',
                                      type=str,
                                      required=False,
                                      help="This field cannot be blank."
                                      )
_transaction_list_parser.add_argument('order_by',
                                      type=str,
                                      required=False,
                                      help="This field cannot be blank."
                                      )

# CREATE TRANSACTION: REQUEST PARSER
_transaction_parser.add_argument('transaction_id',
                                 type=int,
                                 required=False,
                                 help="This field cannot be blank."
                                 )
_transaction_parser.add_argument('amount',
                                 type=int,
                                 required=True,
                                 help="This field cannot be blank."
                                 )
_transaction_parser.add_argument('description',
                                 type=str,
                                 required=True,
                                 help="This field cannot be blank."
                                 )
_transaction_parser.add_argument('service_source',
                                 type=str,
                                 required=True,
                                 help="This field cannot be blank."
                                 )


class Transaction(Resource):
    def post(self):
        data = _transaction_parser.parse_args()

        # Valid transaction from Empire24h
        type24h = data['description'].split()[1].lower()
        if type24h != transaction_type:
            return {"message": "Transaction isn't come from Empire24h"}, 400

        # Valid user
        name = data['description'].split()[0].lower()
        user = UserModel.find_by_username(name.lower())

        if user:
            transaction = TransactionModel(data['amount'], data['description'].lower(), data['service_source'],
                                           1, user.id, getTimeStamp(),
                                           None, None, None)
            transaction.save_to_db()

            user.balance = user.balance + data['amount']
            user.updated_at = getTimeStamp()
            user.save_to_db()
            return transaction.json(), 200

        return {"message": "User not found"}, 404


class TransactionList(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        if not claims["is_admin"]:
            return {"message": "Admin privilege required."}, 401

        transactions = [transaction.json() for transaction in TransactionModel.find_all()]
        user_id = get_jwt_identity()
        if user_id:
            return {
                       "message": "List transaction",
                       "data": [transaction for transaction in transactions],
                       "total": len(TransactionModel.find_all())
                   }, 200
