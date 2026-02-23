# common/permissions.py

def is_teacher(user):
    """
    Teacher 권한 체크용 함수
    - user.role == "teacher" 인지 확인
    """
    return getattr(user, "role", None) == "teacher"