from flask import Flask, request, jsonify
import math
import re

app = Flask(__name__)

# 루트 경로 - Render 배포 헬스 체크용
@app.route("/", methods=["GET"])
def home():
    return "OK", 200

# 숫자만 추출하는 함수
def extract_number(value):
    match = re.search(r'\d+(?:\.\d+)?', str(value))
    return float(match.group()) if match else None

# 체감온도 계산 함수
def calculate_apparent_temp(Ta, RH):
    # Stull 식 기반 습구온도 계산
    try:
        Tw = (
            Ta * math.atan(0.151977 * ((RH + 8.313659) ** 0.5)) +
            math.atan(Ta + RH) -
            math.atan(RH - 1.676331) +
            0.00391838 * (RH ** 1.5) * math.atan(0.023101 * RH) -
            4.686035
        )
    except Exception as e:
        return None, f"습구온도 계산 중 오류 발생: {e}"

    # 체감온도 계산
    apparent_temp = (
        -0.2442 + 0.55399 * Tw + 0.45535 * Ta -
        0.0022 * (Tw ** 2) + 0.00278 * Tw * Ta + 3.0
    )
    apparent_temp = round(apparent_temp, 2)

    # 경보 단계 분류
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

# 카카오 i 스킬 요청 처리
@app.route("/apparent_temp", methods=["POST"])
def handle_request():
    try:
        data = request.get_json()
        print("🔥 받은 데이터:", data)

        params = data.get("action", {}).get("params", {})

        Ta_raw = params.get("Ta")
        RH_raw = params.get("RH")

        Ta = extract_number(Ta_raw)
        RH = extract
