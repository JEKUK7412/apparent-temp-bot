from flask import Flask, request, jsonify
import math
import re

app = Flask(__name__)

def extract_number(value):
    match = re.search(r'\d+(\.\d+)?', str(value))
    return float(match.group()) if match else None

def calculate_wet_bulb_temperature(Ta, RH):
    try:
        Tw = (Ta * math.atan(0.151977 * math.sqrt(RH + 8.313659)) +
              math.atan(Ta + RH) -
              math.atan(RH - 1.67633) +
              0.00391838 * RH ** 1.5 * math.atan(0.023101 * RH) -
              4.686035)
        return Tw
    except Exception as e:
        print(f"Error calculating Tw: {e}")
        return None

def calculate_apparent_temperature(Ta, Tw):
    apparent_temp = -0.2442 + 0.55399 * Tw + 0.45535 * Ta - 0.0022 * Tw ** 2 + 0.00278 * Tw * Ta + 3.0
    return round(apparent_temp, 2)

def determine_warning_level(apparent_temp):
    if apparent_temp >= 38:
        return "위험 단계"
    elif apparent_temp >= 35:
        return "경고 단계"
    elif apparent_temp >= 33:
        return "주의 단계"
    elif apparent_temp >= 31:
        return "관심 단계"
    else:
        return "안전 단계"

@app.route('/apparent_temp', methods=['POST'])
def handle_request():
    try:
        data = request.get_json()
        print("🔥 받은 데이터:", data)

        Ta_raw = data['action']['params'].get('Ta')
        RH_raw = data['action']['params'].get('RH')

        Ta = extract_number(Ta_raw)
        RH = extract_number(RH_raw)

        if Ta is None or RH is None:
            raise ValueError("온도 또는 습도가 유효하지 않습니다.")

        Tw = calculate_wet_bulb_temperature(Ta, RH)
        if Tw is None:
            raise ValueError("습구온도 계산 실패")

        apparent_temp = calculate_apparent_temperature(Ta, Tw)
        warning = determine_warning_level(apparent_temp)

        response_body = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": f"온도 {Ta}℃, 습도 {RH}%의 체감온도는 {apparent_temp}℃, {warning}입니다."
                        }
                    }
                ]
            }
        }
        return jsonify(response_body)

    except Exception as e:
        print("❌ 오류 발생:", e)
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "입력값 오류 또는 처리 중 문제가 발생했습니다."
                        }
                    }
                ]
            }
        }), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
