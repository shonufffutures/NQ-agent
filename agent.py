from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# PASTE YOUR DISCORD WEBHOOK URL BETWEEN THE QUOTES BELOW:
https://discordapp.com/api/webhooks/1553629436623200478/uduG9cs4rr6xKnFYZbV03jkbaWYB690sxRlXRPG9MVETP7I2cyxVEsXv_OGJDWO9NwSW

ACCOUNT_SIZE = 50000
MAX_RISK_PER_TRADE = 300.0  # Max risk per trade in USD

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid Payload"}), 400

    symbol = data.get("symbol", "NQ")
    side = data.get("side")
    price = float(data.get("price"))
    swing_high = float(data.get("swing_high", price + 30))
    swing_low = float(data.get("swing_low", price - 30))
    tf = data.get("tf")

    if side == "BUY":
        sl_price = swing_low
        tp_price = swing_high
        sl_points = abs(price - sl_price)
        tp_points = abs(tp_price - price)
    else:
        sl_price = swing_high
        tp_price = swing_low
        sl_points = abs(sl_price - price)
        tp_points = abs(price - tp_price)

    if sl_points == 0:
        sl_points = 15.0

    rr_ratio = round(tp_points / sl_points, 2)

    nq_risk_single = sl_points * 20.0
    mnq_risk_single = sl_points * 2.0

    mnq_contracts = int(MAX_RISK_PER_TRADE // mnq_risk_single)
    nq_contracts = int(MAX_RISK_PER_TRADE // nq_risk_single)

    if nq_contracts < 1:
        sizing_recommendation = f"⚠️ **Use {mnq_contracts} MNQ Contracts** (NQ risk exceeds max $300 limit)."
    else:
        sizing_recommendation = f"✅ **Use {nq_contracts} NQ Contract(s)** OR **{mnq_contracts} MNQ Contracts**."

    embed = {
        "title": f"🎯 HIGH PROBABILITY {side} | {symbol} ({tf} TF)",
        "color": 3066993 if side == "BUY" else 15158332,
        "fields": [
            {"name": "Setup Type", "value": "HTF OTE Zone + FVG Retracement", "inline": False},
            {"name": "Entry Price", "value": f"`{price:.2f}`", "inline": True},
            {"name": "Stop Loss", "value": f"`{sl_price:.2f}` ({sl_points:.1f} pts)", "inline": True},
            {"name": "Take Profit", "value": f"`{tp_price:.2f}` ({tp_points:.1f} pts)", "inline": True},
            {"name": "Risk / Reward", "value": f"`1 : {rr_ratio}`", "inline": True},
            {"name": "Max USD Risk", "value": f"`${MAX_RISK_PER_TRADE:.2f}`", "inline": True},
            {"name": "Topstep $50k Position Sizing", "value": sizing_recommendation, "inline": False}
        ],
        "footer": {"text": "Topstep Risk Guardrail • 1H/4H/D Execution Model"}
    }

    requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]})
    return jsonify({"status": "alert_sent"}), 200

if __name__ == '__main__':
    app.run(port=5000)
