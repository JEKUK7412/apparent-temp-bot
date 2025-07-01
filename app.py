from flask import Flask, request, jsonify
import math

app = Flask(__name__)

def calculate_wet_bulb_temp(Ta, RH):
    term1 = Ta * math.atan(0.151977 * math.sqrt(RH + 8.313659))
    term2 = math.atan(Ta + RH)
    term3 = math.atan(RH - 1.67633)
    term4 = 0.00391838 * RH ** 1.5 * math.atan(0.023101 * RH)
    Tw = term1 + term2 - term3 + term4 - 4.686035
    return Tw

def calculate_apparent_temp(Ta, RH):
    Tw = calculate_wet_bulb_temp(Ta, RH)
    apparent_temp = (
        -0.2442 + 0.55399 * Tw + 0.45535 * Ta
        - 0.0022 * Tw ** 2 + 0.00278 * Tw * Ta + 3.0
    )
    return round(apparent_temp, 2)

def get_alert_level(temp):
    if temp >= 38:
        return "위험"
    elif temp >= 35:
        return "경고"
    elif temp >= 33:
        return "주의"
    elif temp >= 31:
        return "관심"
    return None

@app.route("/apparent_temp", methods=["POST"])
def handle_request():
    data = request.get_json()
    Ta = int(data['Ta'])
    RH = int(data['RH'])
    apparent = calculate_apparent_temp(Ta, RH)
    level = get_alert_level(apparent)

    if level:
        message = f"온도 {Ta}℃, 습도 {RH}%의 체감온도는 {apparent}℃, {level} 단계입니다."
    else:
        message = f"온도 {Ta}℃, 습도 {RH}%의 체감온도는 {apparent}℃ 입니다."

    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": message}}]
        }
    })

if __name__ == "__main__":
    app.run()
