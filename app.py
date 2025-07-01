from flask import Flask, request, jsonify
import math
import re

app = Flask(__name__)

def extract_number(value):
    """온도나 습도 값에서 숫자만 추출 (예: '35도' → 35)"""
    match = re.search(r'\d+', str(value))
    if match:
        return int(match.group())
    else:
        raise ValueError(f"숫자 추출 실패: {value}")

def calculate_tw(Ta, RH):
    """Stull의 추정식으로 습구온도 계산"""
    try:
        term1 = Ta * math.atan(0.151977 * math.sqrt(RH + 8.313659))
        term2 = math.atan(Ta + RH)
        term3 = math.atan(RH - 1.67633)
        term4 = 0.00391838 * RH ** 1.5 * math.atan(0.023101 * RH)
        Tw = term1 + term2 - term3 + term4 - 4.686035
        return Tw
    except Exception as e:
        raise ValueError(f"습구온도 계산 실패: {e}")

def calculate_apparent_temp(Ta, Tw):
    """체감온도 계산식"""
    return -0.2442 + 0.55399 * Tw + 0.45535 * Ta - 0.0022 * (Tw ** 2) + 0.00278 * Tw * Ta + 3.0

def get_alert_level(apparent_temp):
    """KOSHA 기준 체감온도 단계"""
    if apparent_temp >= 38:
        return "위험"
    elif apparent_temp >= 35:
        return "경고"
    elif apparent_temp >= 33:
        return "주의"
    elif apparent_temp >= 31:
        return "관심"
    else:
        return "정상"

@app.route('/apparent_temp', methods=['POST'])
def handle_request():
    try:
        data = request.get_json()
        print("🔥 받은 데이터:", data)

        # 파라미터에서 값 추출
        params = data['action']['params']
        Ta_raw = params.get('Ta')
        RH_raw = params.get('RH')

        # 숫자 추출
        Ta = extract_number(Ta_raw)
        RH = extract_number(RH_raw)

        # 계산
        Tw = calculate_tw(Ta, RH)
        apparent_temp = calculate_apparent_temp(Ta, Tw)
        level = get_alert_level(apparent_temp)

        # 결과 텍스트
        response_text = f"온도 {Ta}℃, 습도 {RH}%의 체감온도는 {apparent_temp:.2f}℃, {level} 단계입니다."

        return jsonify({
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
        })

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
