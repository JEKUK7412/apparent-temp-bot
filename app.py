from flask import Flask, request, jsonify
import math
import re

app = Flask(__name__)


def calculate_apparent_temperature(Ta, RH):
    # Stull의 추정식을 이용한 Tw 계산
    Tw = (
        Ta * math.atan(0.151977 * math.sqrt(RH + 8.313659))
        + math.atan(Ta + RH)
        - math.atan(RH - 1.67633)
        + 0.00391838 * RH ** 1.5 * math.atan(0.023101 * RH)
        - 4.686035
    )

    # 체감온도 계산식
    apparent_temp = (
        -0.2442 + 0.55399 * Tw + 0.45535 * Ta
        - 0.0022 * Tw ** 2 + 0.00278 * Tw * Ta + 3.0
    )

    return round(apparent_temp, 2)


def get_warning_level(apparent_temp):
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
        req_data = request.get_json()
        print("\U0001F525 받은 데이터:", req_data)

        data = req_data['action']['params']

        # 오픈빌더 기본 엔티티명으로 추출
        Ta_raw = data.get('sys.unit.temperature')
        RH_raw = data.get('sys.number.percent')

        # 정수값 추출
        Ta = int(re.search(r'\d+', Ta_raw).group()) if Ta_raw else None
        RH = int(re.search(r'\d+', RH_raw).group()) if RH_raw else None

        if Ta is None or RH is None:
            raise ValueError("Ta 또는 RH 값이 없습니다.")

        apparent_temp = calculate_apparent_temperature(Ta, RH)
        level = get_warning_level(apparent_temp)

        response_text = f"온도 {Ta}\u2103, 습도 {RH}%의 체감온도는 {apparent_temp}\u2103, {level} 단계입니다."

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
        print("\u274c 오류 발생:", e)
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
