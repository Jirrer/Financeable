import os
from flask import Flask, jsonify, request
import src.getTransactions

app = Flask(__name__)

@app.route("/get-report", methods=['POST'])
def getTransations():
    if 'report' not in request.files: return 'No file', 400
    
    report = request.files['report']

    if request.form['flipValues'].lower() == 'true':
        flipValues = True

    elif request.form['flipValues'].lower() == 'false':
        flipValues = False

    else:
        return jsonify({'Status': 'Fail', 'Message': "Invalid value for 'flipValues'"}), 404

    match request.form['returnType'].upper():
        case 'JSON': returnType = src.getTransactions.ReturnType.JSON
        case '': return jsonify({'Status': 'Fail', 'Message': "Null Return Type"}), 404
        case _: return jsonify({'Status': 'Fail', 'Message': "Invalid Return Type"}), 403
        
    transactions = src.getTransactions.run(report, flipValues, returnType)

    return jsonify({"Status": "Success", "transactions": transactions}), 200


if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_RUN_PORT", "5001"))
    app.run(debug=True, host=host, port=port)