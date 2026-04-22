class MasterSlaveRouter:
    """
    읽기는 'replica'로, 쓰기/수정은 'default'로 보내는 DB 라우터
    """
    def db_for_read(self, model, **hints):
        return 'replica'

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # 테이블 생성(마이그레이션)은 무조건 default(쓰기)에만!
        return db == 'default'