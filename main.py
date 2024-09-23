import logging
import os
from flask import Flask, render_template, request, jsonify
from models.legal_analyzer import ComplianceAuditor
from werkzeug.exceptions import RequestTimeout
import time
from database import add_assessment, get_assessment_by_input

app = Flask(__name__)
compliance_auditor = ComplianceAuditor()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up database URL
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
        analysis_result = compliance_auditor.analyze(user_input)
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

@app.route("/test_database", methods=["GET"])
def test_database():
    try:
        # Test adding an assessment
        test_input = "这是一个测试输入"
        test_issues = ["测试问题1", "测试问题2"]
        test_laws = ["测试法律1", "测试法律2"]
        
        add_assessment(test_input, test_issues, test_laws)
        logger.info("Test assessment added to the database")

        # Test retrieving the assessment
        retrieved_assessment = get_assessment_by_input(test_input)
        
        if retrieved_assessment:
            logger.info("Test assessment retrieved successfully")
            return jsonify({"success": True, "retrieved_assessment": retrieved_assessment}), 200
        else:
            logger.warning("Failed to retrieve test assessment")
            return jsonify({"success": False, "error": "Failed to retrieve test assessment"}), 500

    except Exception as e:
        logger.error(f"Error during database test: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
