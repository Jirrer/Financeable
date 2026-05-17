import os
from flask import Flask, jsonify, request
import src.GenerateData, src.PullTransactions

app = Flask(__name__)

@app.route("/get-report", methods=['POST'])
def getTransations():
    if 'report' not in request.files: return 'No file', 400
    
    report = request.files['report']

    transactions = src.PullTransactions.run('fifth_third', report)

    categorizedTransactions = src.GenerateData.Run('01/2026', transactions)


    return jsonify({"Status": "Success", "transactions": categorizedTransactions}), 200




if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_RUN_PORT", "5001"))
    app.run(debug=True, host=host, port=port)