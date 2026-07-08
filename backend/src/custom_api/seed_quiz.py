"""data/quiz.json을 Quiz 데이터베이스에 적재하는 1회성 시드 스크립트.
seed_prices.py, seed_news.py와 동일한 위치/실행 방식: `python3 seed_quiz.py`를 custom_api 디렉터리에서 실행.
이미 Quiz에 데이터가 있으면 아무것도 하지 않는다(재실행 안전).
"""
import json

import account
import quiz


def run():
    with open("data/quiz.json", encoding="utf-8") as f:
        data = json.load(f)

    if account.session.query(quiz.QuizEntry).count() > 0:
        print("Quiz already has data, skipping seed.")
        return

    quiz_list = data.get("quizList", [])

    for q in quiz_list:
        quiz_body = {
            "question": q["question"],
            "options": q["options"]
        }

        account.session.add(quiz.QuizEntry(
            Quiz_Num=q["quizNum"],
            Quiz_Body=quiz_body,
            Quiz_Answer=q["answerIndex"]
        ))

    account.session.commit()
    print(f"Seeded {len(quiz_list)} quiz questions.")


if __name__ == "__main__":
    run()
