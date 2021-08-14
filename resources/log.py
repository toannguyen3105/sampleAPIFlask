from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from models.log import LogModel


class LogList(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401

        user_id = get_jwt_identity()
        logs = [user.json() for user in LogModel.find_all()]

        if user_id:
            return {
                       "message": "Danh sách log thành công",
                       "data": [log for log in logs],
                       "total": len(LogModel.find_all())
                   }, 200
        else:
            return {
                       "message": "More data available if you log in.",
                       "data": [log['message'] for log in logs],
                       "total": len(LogModel.find_all())
                   }, 200
