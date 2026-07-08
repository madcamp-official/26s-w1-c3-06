"""data/quiz.json을 Quiz 데이터베이스에 반영하는 시드 스크립트.
seed_prices.py, seed_news.py와 동일한 위치/실행 방식: `python3 seed_quiz.py`를 custom_api 디렉터리에서 실행.
이미 Quiz에 데이터가 있어도 quiz.json 기준으로 문제와 정답을 업데이트한다.
"""
import json

import account
import quiz


def run():
    with open("data/quiz.json", encoding="utf-8") as f:
        data = json.load(f)

    quiz_list = data.get("quizList", [])

    for q in quiz_list:
        quiz_body = {
            "question": q["question"],
            "options": q["options"]
        }

        quiz_entry = account.session.get(quiz.QuizEntry, q["quizNum"])
        if quiz_entry:
            quiz_entry.Quiz_Body = quiz_body
            quiz_entry.Quiz_Answer = q["answerIndex"]
        else:
            account.session.add(quiz.QuizEntry(
                Quiz_Num=q["quizNum"],
                Quiz_Body=quiz_body,
                Quiz_Answer=q["answerIndex"]
            ))

    account.session.commit()
    print(f"Synced {len(quiz_list)} quiz questions.")


if __name__ == "__main__":
    run()
