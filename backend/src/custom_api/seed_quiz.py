"""
Quiz 테이블 시드 스크립트.

GET /quiz(account.DailyBailout)가 `floor(random() * count(Quiz))`로 Quiz_Num을
뽑아 session.get(QuizEntry, quiz_num)으로 조회하기 때문에, Quiz_Num은 반드시
0부터 (문제 수 - 1)까지 빈 자리 없이 이어져야 한다.

실행:
    python seed_quiz.py
"""

from quiz import Base, QuizEntry, engine, session

QUIZZES = [
    {
        "question": "'매수'는 무슨 뜻일까요?",
        "options": ["주식을 사는 것", "주식을 파는 것", "주식을 보관하는 것", "주식을 등록하는 것"],
        "answer": 0,
    },
    {
        "question": "'매도'는 무슨 뜻일까요?",
        "options": ["주식을 더 사는 것", "주식을 팔아서 현금으로 바꾸는 것", "회사에 취업하는 것", "배당금을 받는 것"],
        "answer": 1,
    },
    {
        "question": "'평균 매수가'는 무엇을 뜻할까요?",
        "options": ["오늘 이 주식의 최고가", "내가 이 주식을 산 가격의 평균", "이 회사의 평균 매출", "친구들이 산 평균 가격"],
        "answer": 1,
    },
    {
        "question": "수익률이 '+5%'라는 건 무슨 뜻일까요?",
        "options": ["산 가격보다 5% 떨어졌다", "산 가격보다 5% 올랐다", "5원이 늘었다", "5주를 더 샀다"],
        "answer": 1,
    },
    {
        "question": "'배당금'은 무엇일까요?",
        "options": ["회사가 주주에게 나눠주는 이익금", "주식을 살 때 내는 수수료", "주가가 오를 확률", "주식을 파는 세금"],
        "answer": 0,
    },
    {
        "question": "'시가총액'은 무엇을 뜻할까요?",
        "options": ["하루 동안 거래된 주식 수", "주가 × 총 발행 주식 수로 계산한 회사의 규모", "회사의 연간 매출액", "주식 한 주의 가격"],
        "answer": 1,
    },
    {
        "question": "'코스피(KOSPI)'는 무엇일까요?",
        "options": ["개별 종목의 이름", "우리나라 유가증권시장의 대표 주가지수", "증권사의 이름", "주식 계좌의 종류"],
        "answer": 1,
    },
    {
        "question": "'손절매(손절)'는 무슨 뜻일까요?",
        "options": ["손해를 보기 전에 더 사는 것", "손실을 확정하고 주식을 파는 것", "이익을 실현하고 파는 것", "배당금을 포기하는 것"],
        "answer": 1,
    },
    {
        "question": "여러 종목에 나눠서 투자하는 '분산투자'를 하는 주된 이유는 무엇일까요?",
        "options": ["세금을 더 많이 내기 위해", "한 종목의 손실 위험을 줄이기 위해", "거래 수수료를 늘리기 위해", "주식을 더 빨리 팔기 위해"],
        "answer": 1,
    },
    {
        "question": "'지정가 주문'은 무엇을 뜻할까요?",
        "options": ["시장에 나온 현재 가격으로 즉시 사고파는 주문", "내가 원하는 가격을 정해서 사고파는 주문", "무조건 다음 날 체결되는 주문", "수수료가 없는 주문"],
        "answer": 1,
    },
]


def seed():
    Base.metadata.create_all(engine)

    if session.query(QuizEntry).count() > 0:
        print("Quiz 테이블에 이미 데이터가 있어 시딩을 건너뜁니다.")
        return

    for quiz_num, q in enumerate(QUIZZES):
        entry = QuizEntry(
            Quiz_Num=quiz_num,
            Quiz_Body={"question": q["question"], "options": q["options"]},
        )
        entry.Quiz_Answer = q["answer"]
        session.add(entry)

    session.commit()
    print(f"퀴즈 {len(QUIZZES)}개를 시딩했습니다.")


if __name__ == "__main__":
    seed()
