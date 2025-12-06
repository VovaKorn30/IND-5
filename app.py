from flask import Flask, jsonify
import logging
import logging.handlers
import socket
import time

app = Flask(__name__)

# -----------------------
# Logging configuration
# -----------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()  # вивід також у консоль
    ]
)

# -----------------------
# UDP client for StatsD
# -----------------------
UDP_IP = "127.0.0.1"
UDP_PORT = 9999

def send_statsd(message: str):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
        logging.info(f"Sent StatsD message: {message}")
    except Exception as e:
        logging.error(f"Failed to send StatsD message: {e}")

# -----------------------
# Application state
# -----------------------
start_time = time.time()
request_count = 0

# -----------------------
# Routes
# -----------------------
@app.before_request
def before_request():
    global request_count
    request_count += 1

@app.route('/')
def home():
    logging.info("Accessed '/' route")
    return "Сервіс працює"

@app.route('/error')
def error():
    try:
        logging.warning("Accessed '/error' route - about to trigger exception")
        1 / 0  # спеціально викликаємо помилку
    except Exception as e:
        logging.exception("An exception occurred in '/error'")
        send_statsd(f"error:{str(e)}")
        return "Виникла помилка, про яку повідомлено в StatsD", 500

@app.route('/status')
def status():
    uptime = time.time() - start_time
    logging.info("Accessed '/status' route")
    return jsonify({
        "uptime_seconds": round(uptime, 2),
        "request_count": request_count
    })

# -----------------------
# Run the app
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)
