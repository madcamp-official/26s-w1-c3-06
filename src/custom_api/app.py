from flask import Flask, request, jsonify

import account

app = Flask(__name__)


# 로컬에서 프론트(file:// 또는 다른 포트)와 붙여서 테스트할 수 있도록 CORS 허용
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/auth/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}

    nickname = data.get("nickname")
    id_ = data.get("id")
    pw = data.get("pw")

    if not nickname or not id_ or not pw:
        return jsonify({"message": "닉네임, 아이디, 비밀번호를 모두 입력해주세요"}), 400

    user = account.create(id_, pw, nickname)

    if user is None:
        return jsonify({"message": "이미 사용 중인 아이디 또는 닉네임입니다"}), 409

    return jsonify({"id": user.ID, "nickname": user.Nickname}), 201


@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    id_ = data.get("id")
    pw = data.get("pw")

    if not id_ or not pw:
        return jsonify({"message": "아이디와 비밀번호를 입력해주세요"}), 400

    user = account.authenticate(id_, pw)

    if user is None:
        return jsonify({"message": "아이디 또는 비밀번호가 올바르지 않습니다"}), 401

    # TODO: 실제 세션/JWT 발급으로 교체. 지금은 로그인 성공 여부 확인용 자리표시자
    return jsonify({"id": user.ID, "token": "dev-token"}), 200


@app.route("/auth/check-id", methods=["GET"])
def check_id():
    id_ = request.args.get("id", "")
    return jsonify({"available": not account.id_exists(id_)}), 200


@app.route("/auth/check-nickname", methods=["GET"])
def check_nickname():
    nickname = request.args.get("nickname", "")
    return jsonify({"available": not account.nickname_exists(nickname)}), 200


if __name__ == "__main__":
    app.run(debug=True, port=8000)
