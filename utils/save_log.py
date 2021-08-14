from models.log import LogModel


def SaveLogTable(user_id, ip_target, message, description, status, created_at, created_by, updated_at, updated_by):
    log = LogModel(user_id, ip_target, message, description, status, created_at, created_by, updated_at, updated_by)
    log.save_to_db()
