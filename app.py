from flask import Flask, request, jsonify
import math

app = Flask(__name__)

@app.route("/apparent_temp", methods=["POST"])
def handle_request():
    try:
        data = request.get_json()

        # 파라미터 값 읽기
        Ta = float(data["action"]["params"]["Ta"])
        RH = float(data["action"]["params"]["RH"])

        # 습구온도 추정 (Stull의 식)
        Tw = (
            Ta * math.atan(0.151977 * math.sqrt(RH + 8.313659)) +
            math.atan(Ta + RH) -
            math.atan(RH - 1.67633) +
            0.00391838 * RH ** 1.5 * math.atan(0.023101 * RH) -
            4.686035
        )

        # 체감온도 계산
        apparent_temp = (
            -0.2442 + 0.55399 * Tw + 0.45535 * Ta -
            0.0022 * Tw ** 2 + 0.00278 * Tw * Ta + 3.0
        )

        apparent_temp = round(apparent_temp, 2)

        # 경보 단계 판별
        if apparent_temp >= 38:
            level = "위험 단계"
        elif apparent_temp >= 35:
            level = "경고 단계"
        elif apparent_temp >= 33:
            level = "주의 단계"
        elif apparent_temp >= 31:
            level = "관심 단계"
        else:
            level = ""

        # 응답 메시지 구성
        if level:
            message = f"온도 {Ta}℃, 습도 {RH}%의 체감온도는 {apparent_temp}℃, {level}입니다."
        else:
            message = f"온도 {Ta}℃, 습도 {RH}%의 체감온도는 {apparent_temp}℃ 입니다."

        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {
                        "text": message
                    }
                }]
            }
        })

    except Exception as e:
        print("🔥 에러 발생:", e)
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {
                        "text": "⚠️ 오류가 발생했습니다. 입력값을 다시 확인해주세요."
                    }
                }]
            }
        }), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
