from flask import Flask, request, jsonify
import math
import re

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "OK", 200

def extract_number(value):
    match = re.search(r'\d+(?:\.\d+)?', str(value))
    return float(match.group()) if match else None

def calculate_apparent_temp(Ta, RH):
    try:
        Tw = (
            Ta * math.atan(0.151977 * ((RH + 8.313659) ** 0.5)) +
            math.atan(Ta + RH) -
            math.atan(RH - 1.676331) +
            0.00391838 * (RH ** 1.5) * math.atan(0.023101 * RH) -
            4.686035
        )
    except Exception as e:
        return None, f"습구온도 계산 오류: {e}"

    apparent_temp = (
        -0.2442 + 0.55399 * Tw + 0.45535 * Ta -
        0.0022 * (Tw ** 2) + 0.00278 * Tw * Ta + 3.0
    )
    apparent_temp = round(apparent_temp, 2)

    if apparent_temp >= 38:
        level = "위험"
    elif apparent_temp >= 35:
        level = "경고"
    elif apparent_temp >= 33:
        level = "주의"
    elif apparent_temp >= 31:
        level = "관심"
    else:
        level = "정보 없음"

    return apparent_temp, level

@app.route("/apparent_temp", methods=["POST"])
def handle_request():
    try:
        data = request.get_json()
        print("🔥 받은 데이터:", data)

        params = data.get("action", {}).get("params", {})

        Ta_raw = params.get("Ta")
        RH_raw = params.get("RH")

        Ta = extract_number(Ta_raw)
        RH = extract_number(RH_raw)

        if Ta is None or RH is None:
            raise ValueError("온도(Ta) 또는 습도(RH)를 숫자로 추출할 수 없습니다.")

        apparent_temp, level = calculate_apparent_temp(Ta, RH)

        if apparent_temp is None:
            raise ValueError(level)

        response_text = f"온도 {Ta}℃, 습도 {RH}%의 체감온도는 {apparent_temp}℃, {level} 단계입니다."

    except Exception as e:
        print("❌ 오류 발생:", str(e))
        response_text = "입력값을 정확히 인식하지 못했습니다. 예: '온도 30도 습도 70%' 와 같이 입력해주세요."

    response = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": response_text
                    }
                }
            ]
        }
    }

    return jsonify(response)
