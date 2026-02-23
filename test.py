import os
import django
import random

# 1. Django 환경 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")  # <--- 프로젝트 settings 경로 확인
django.setup()

from course.models import Course
from django.contrib.auth import get_user_model

User = get_user_model()

# 2. 강의 생성
def create_test_courses(n=100):
    # 테스트용 teacher: 첫 번째 관리자 계정 가져오기
    teacher = User.objects.first()
    if not teacher:
        print("먼저 User(teacher) 계정을 만들어주세요!")
        return

    categories = ['국어', '수학', '영어', '사회', '과학', '기타']

    for i in range(1, n+1):
        title = f"테스트 강의 {i}"
        description = f"이것은 테스트용 강의 {i}번의 설명입니다."
        price = random.choice([0, 10000, 20000, 30000])
        category = random.choice(categories)

        course = Course.objects.create(
            title=title,
            description=description,
            price=price,
            teacher=teacher,
            category=category
        )
        # 테스트용: 학생 0~5명 랜덤 등록
        students = list(User.objects.exclude(id=teacher.id))
        selected_students = random.sample(students, k=min(len(students), random.randint(0,5)))
        course.students.set(selected_students)

    print(f"{n}개의 테스트 강의를 생성했습니다!")

# 3. 실행
if __name__ == "__main__":
    create_test_courses(100)