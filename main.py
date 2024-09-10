import logging
from flask import Flask, render_template, request, jsonify
from models.legal_analyzer import LegalAnalyzer
from werkzeug.exceptions import RequestTimeout
import time

app = Flask(__name__)
legal_analyzer = LegalAnalyzer()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    start_time = time.time()
    timeout = 30  # Set timeout to 30 seconds

    try:
        user_input = request.json.get("input", "")
        logger.info(f"Received input: {user_input[:100]}...")  # Log the first 100 characters of input

        if not user_input:
            logger.warning("No input provided")
            return jsonify({"error": "请输入您的情况描述"}), 400

        logger.info("Analyzing input")
        analysis_result = legal_analyzer.analyze(user_input)
        logger.info(f"Analysis result: {analysis_result}")

        # Check if the request has exceeded the timeout
        if time.time() - start_time > timeout:
            logger.error("Analysis timed out")
            raise RequestTimeout("分析时间过长，请尝试缩短输入文本或稍后重试")

        logger.info("Analysis completed successfully")
        return jsonify(analysis_result)

    except RequestTimeout as e:
        logger.error(f"Request timed out: {str(e)}")
        return jsonify({"error": str(e)}), 408
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)
        return jsonify({"error": "分析过程中出现错误，请稍后重试"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
