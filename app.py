from flask import Flask, request, jsonify
import math
import json
import re

app = Flask(__name__)

def extract_number(value):
    """문자열에서 숫자만 추출 (정수 또는 소수점)"""
    match = re.search(r"[-+]?\d*\.?\d+", value)
    return float(match.group()) if match else None

def calculate_wet_bulb_temperature(Ta, RH):
    return (Ta * math.atan(0.151977 * (RH + 8.313659)**0.5) +
            math.atan(Ta + RH) -
            math.atan(RH - 1.67633) +
            0.00391838 * RH**1.5 * math.atan(0.023101 * RH) -
            4.686035)

def calculate_apparent_temperature(Ta, RH):
    Tw = calculate_wet_bulb_temperature(Ta, RH)
    return (-0.2442 + 0.55399 * Tw + 0.45535 * Ta -
            0.0022 * Tw**2 + 0.00278 * Tw * Ta + 3.0)

@app.route("/apparent_temp", methods=["POST"])
def handle_request():
    data = request.get_json()
    print("🔥 받은 데이터:", json.dumps(data, ensure_ascii=False, indent=2))

    try:
        params = data['action']['detailParams']
        # sys.unit.temperature와 sys.number.percent 파라미터명에 따라 추출
        temp_str = params['sys.unit.temperature']['origin']
        humid_str = params['sys.number.percent']['origin']

        Ta = extract_number(temp_str)  # "30도" → 30.0
        RH = extract_number(humid_str) # "55%" → 55.0

        if Ta is None or RH is None:
            raise ValueError("온도와 습도를 올바르게 입력해주세요.")

        apparent_temp = calculate_apparent_temperature(Ta, RH)
        apparent_temp = round(apparent_temp, 2)

        # 경보 단계 판단 (기상청 기준)
        if apparent_temp >= 41:
            level = "위험"
        elif apparent_temp >= 35:
            level = "경고"
        elif apparent_temp >= 33:
            level = "주의"
        elif apparent_temp >= 31:
            level = "관심"
        else:
            level = "정상"

        response = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": f"온도 {Ta}℃, 습도 {RH}%의 체감온도는 {apparent_temp}℃, {level} 단계입니다."
                        }
                    }
                ]
            }
        }

        return jsonify(response)

    except Exception as e:
        print("❌ 오류 발생:", str(e))
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "입력값을 처리하는 중 오류가 발생했습니다. 예: 30도 55%처럼 입력해주세요."
                        }
                    }
                ]
            }
        }), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
