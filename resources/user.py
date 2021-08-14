#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_restful import Resource, reqparse
from validate_email import validate_email

# UserRegister to validate email =)))
class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("email",
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    def post(self):
        data = self.parser.parse_args()

        email = data["email"]

        is_valid = validate_email(email, verify=True)
        return {
            "status": 200,
            "message": "Success",
            "data": is_valid
        }, 200
