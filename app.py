from flask import Flask, request, jsonify
import math
import json

app = Flask(__name__)

@app.route("/apparent_temp", methods=["POST"])
def handle_request():
    data = request.get_json()
    print("🔥 받은 데이터:", json.dumps(data, ensure_ascii=False, indent=2))

    try:
        # detailParams에서 origin 값을 꺼내 숫자로 변환
        Ta = float(data['action']['detailParams']['Ta']['origin'])
        RH = float(data['action']['detailParams']['RH']['origin'])

        # Stull 식 기반 체감온도 계산
        apparent_temp = Ta + 0.33 * RH - 0.70
        apparent_temp = round(apparent_temp, 2)

        # 경보 단계 판단
        if apparent_temp >= 38:
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
                            "text": "입력값을 처리하는 중 오류가 발생했습니다. 숫자로 된 온도와 습도를 정확히 입력해주세요."
                        }
                    }
                ]
            }
        }), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
