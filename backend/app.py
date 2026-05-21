import os
from flask import Flask, jsonify, request
import src.getTransactions as getTransactions
import src.uploadTransaction as uploadTransaction
import src.pullReport as pullReport

app = Flask(__name__)

@app.route("/create-report", methods=['POST'])
def get_transations():
    if 'report' not in request.files: return 'No file', 400
    
    report = request.files['report']

    if not request.form['internal_transfers']:
        internal_transfers = set()

    else:
        internal_transfers = set(request.form['internal_transfers'].split(','))

    match request.form['returnType'].upper():
        case 'JSON': returnType = getTransactions.ReturnType.JSON
        case '': return jsonify({'Status': 'Fail', 'Message': "Null Return Type"}), 404
        case _: return jsonify({'Status': 'Fail', 'Message': "Invalid Return Type"}), 403
        
    transactions = getTransactions.run(report, returnType, internal_transfers)

    return jsonify({"Status": "Success", "transactions": transactions}), 200

@app.route("/upload-report", methods=['POST'])
def upload_report():
    data = request.json

    if 'user_id' not in data: return 'null id', 400

    if 'transactions' not in data: return 'null transactions', 400

    try:
        uploadTransaction.run(data['user_id'], data['transactions'])

        return jsonify({"Status": "Success"}), 200

    except Exception as e:
        print(e)
        return str(e), 500
    
@app.route("/get-report", methods=["GET"])
def get_report():
    user_id = request.args.get("id", type=str)
    input_type = request.args.get("input_type", type=str)
    date = request.args.get("date", type=str)
    return_type = request.args.get("return_type", type=str)

    if not user_id:
        return jsonify({"error": "Missing user id"}), 400
    

    try:
        report = pullReport.run(userID=user_id, inputType=input_type, date=date, returnType=return_type)

        return jsonify({'status': 'success', 'report': report}), 200
    except Exception as e:
        print(e)
        return str(e), 500


if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_RUN_PORT", "5001"))
    app.run(debug=True, host=host, port=port)