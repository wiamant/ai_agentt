from flask import Flask, request, jsonify, render_template, session
from ai_agent import AIAgent
from database import Database
from telecom_api import TelecomAPI

app = Flask(__name__)
app.secret_key = "dev-secret-key"

# ======================
# INIT - IMPORTANT : passer db et telecom à l'agent
# ======================
db = Database()
telecom = TelecomAPI(db)
agent = AIAgent(db=db, telecom=telecom)  # CHANGEMENT ICI

# ======================
# PAGE PRINCIPALE
# ======================
@app.route('/')
def index():
    return render_template('index.html')


# ======================
# AUTHENTIFICATION
# ======================
@app.route('/api/auth', methods=['POST'])
def auth():
    data = request.json
    msisdn = data.get('msisdn')

    if not msisdn:
        return jsonify({"success": False, "message": "Numéro manquant"}), 400

    client = db.get_client(msisdn)

    if not client:
        return jsonify({"success": False, "message": "Client non trouvé"}), 404

    session['msisdn'] = client['msisdn']

    return jsonify({
        "success": True,
        "client": {
            "msisdn": client['msisdn'],
            "nom": client['nom']
        }
    })


# ======================
# LOGOUT
# ======================
@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True})


# ======================
# CHATBOT - CHANGEMENT ICI
# ======================
@app.route('/api/chat', methods=['POST'])
def chat():
    if 'msisdn' not in session:
        return jsonify({"message": "Veuillez vous authentifier"}), 401

    data = request.json
    message = data.get('message', '')

    # Passer le msisdn à l'agent
    response = agent.process(message, msisdn=session['msisdn'])
    return jsonify(response)


# ======================
# ACTIONS TÉLÉCOM
# ======================
@app.route('/api/action/activate-bundle', methods=['POST'])
def activate_bundle():
    if 'msisdn' not in session:
        return jsonify({"success": False, "error": "Non authentifié"}), 401

    data = request.json
    bundle_id = data.get('bundle_id')

    result = telecom.activate_data_bundle(session['msisdn'], bundle_id)
    return jsonify(result)


@app.route('/api/action/cancel-bundle', methods=['POST'])
def cancel_bundle():
    if 'msisdn' not in session:
        return jsonify({"success": False, "error": "Non authentifié"}), 401

    data = request.json
    bundle_id = data.get('bundle_id')

    result = telecom.cancel_bundle(session['msisdn'], bundle_id)
    return jsonify(result)


@app.route('/api/action/get-balance', methods=['POST'])
def get_balance():
    if 'msisdn' not in session:
        return jsonify({"success": False, "error": "Non authentifié"}), 401

    result = telecom.get_balance(session['msisdn'])
    return jsonify(result)


@app.route('/api/action/recharge', methods=['POST'])
def recharge():
    if 'msisdn' not in session:
        return jsonify({"success": False, "error": "Non authentifié"}), 401

    data = request.json
    montant = data.get('montant')

    result = telecom.recharge(session['msisdn'], montant)
    return jsonify(result)


@app.route('/api/action/suspend', methods=['POST'])
def suspend_line():
    if 'msisdn' not in session:
        return jsonify({"success": False, "error": "Non authentifié"}), 401

    result = telecom.suspend_line(session['msisdn'])
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)