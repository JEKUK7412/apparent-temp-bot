from flask import Flask, request, jsonify
import math

app = Flask(__name__)

# 습구온도 계산 (Stull 공식)
def calculate_tw(Ta, RH):
    return (
        Ta * math.atan(0.151977 * math.sqrt(RH + 8.313659)) +
        math.atan(Ta + RH) -
        math.atan(RH - 1.67633) +
        0.00391838 * math.pow(RH, 1.5) * math.atan(0.023101 * RH) -
        4.686035
    )

# 체감온도 계산식
def calculate_apparent_temp(Ta, Tw):
    return (
        -0.2442 +
        0.55399 * Tw +
        0.45535 * Ta -
        0.0022 * (Tw ** 2) +
        0.00278 * Tw * Ta +
        3.0
    )

# 경보 단계 판정
def get_alert_level(apparent_temp):
    if apparent_temp >= 38:
        return "위험 단계"
    elif apparent_temp >= 35:
        return "경고 단계"
    elif apparent_temp >= 33:
        return "주의 단계"
    elif apparent_temp >= 31:
        return "관심 단계"
    else:
        return None

@app.route("/apparent_temp", methods=["POST"])
def handle_request():
    try:
        data = request.get_json()
        print("🔥 받은 데이터:", data)

        # 파라미터 가져오기
        Ta = float(data['action']['params']['Ta'])
        RH = float(data['action']['params']['RH'])

        Tw = calculate_tw(Ta, RH)
        apparent_temp = calculate_apparent_temp(Ta, Tw)
        apparent_temp_rounded = round(apparent_temp, 2)
        alert = get_alert_level(apparent_temp)

        if alert:
            message = f"온도 {Ta}℃, 습도 {RH}%의 체감온도는 {apparent_temp_rounded}℃, {alert}입니다."
        else:
            message = f"온도 {Ta}℃, 습도 {RH}%의 체감온도는 {apparent_temp_rounded}℃입니다."

        print("📤 응답 메시지:", message)

        # 카카오 i 오픈빌더 응답 포맷
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": message
                        }
                    }
                ]
            }
        })

    except Exception as e:
        print("🔥 에러 발생:", e)
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "⚠️ 처리 중 오류가 발생했습니다. 입력을 확인해주세요."
                        }
                    }
                ]
            }
        }), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
