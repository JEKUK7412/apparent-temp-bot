from flask import Flask, request, jsonify
import math

app = Flask(__name__)

@app.route('/apparent_temp', methods=['POST'])
def handle_request():
    try:
        data = request.get_json()
        print("🔥 받은 데이터:", data)

        # 액션 파라미터 받아오기
        params = data['action']['params']

        # 온도: "30도" → 30, 습도: "60%" → 60
        temp_raw = params.get('sys_unit_temperature', '0')
        humid_raw = params.get('sys_number_percent', '0')

        # 숫자만 추출
        Ta = float(''.join(filter(str.isdigit, str(temp_raw))))
        RH = float(''.join(filter(str.isdigit, str(humid_raw))))

        # Stull의 추정식을 통한 습구온도(Tw) 계산
        Tw = Ta * math.atan(0.151977 * math.sqrt(RH + 8.313659)) \
             + math.atan(Ta + RH) - math.atan(RH - 1.67633) \
             + 0.00391838 * RH**1.5 * math.atan(0.023101 * RH) - 4.686035

        # 체감온도 계산
        apparent_temp = round(-0.2442 + 0.55399 * Tw + 0.45535 * Ta - 0.0022 * Tw**2 + 0.00278 * Tw * Ta + 3.0, 2)

        # 경보 단계 판별
        if apparent_temp >= 38:
            level = "위험"
        elif apparent_temp >= 35:
            level = "경고"
        elif apparent_temp >= 33:
            level = "주의"
        elif apparent_temp >= 31:
            level = "관심"
        else:
            level = "안전"

        # 응답 구성
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": f"온도 {int(Ta)}℃, 습도 {int(RH)}%의 체감온도는 {apparent_temp}℃, {level} 단계입니다."
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
