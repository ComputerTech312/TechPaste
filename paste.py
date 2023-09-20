from flask import Flask, request, render_template, url_for
from datetime import datetime, timedelta
import secrets
import string

app = Flask(__name__)

pastes = {}

# Function to generate a random ID of a given length
def generate_random_id(length=16):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def parse_expiry_time(expiry_option):
    expiry_time = None
    if expiry_option == "1_minute":
        expiry_time = datetime.now() + timedelta(minutes=1)
    elif expiry_option == "5_minute":
        expiry_time = datetime.now() + timedelta(minutes=5)
    elif expiry_option == "10_minute":
        expiry_time = datetime.now() + timedelta(minutes=10)
    elif expiry_option == "1_hour":
        expiry_time = datetime.now() + timedelta(hours=1)
    elif expiry_option == "1_day":
        expiry_time = datetime.now() + timedelta(days=1)
    else:
        expiry_time = datetime.now() + timedelta(days=1)
    return expiry_time

@app.route("/api/v1/secure-paste", methods=["POST"])
def secure_paste():
    if request.method == "POST":
        if not "data" in request.json:
            print("no data key")
            return {"success": False}, 400
        id = generate_random_id()
        expiry_time = parse_expiry_time(request.json.get("expiry", "1_day"))
        pastes[id] = {"content": request.json["data"], "expiry": expiry_time}
        return {
            "success": True,
            "id": id
        }
    
@app.route("/api/v1/secure-paste/<paste_id>", methods=["GET"])
def secure_paste2(paste_id):
    if request.method == "GET":
        print(pastes)
        print(request.args)
        paste_data = pastes.get(paste_id)
        if paste_data is not None:
            if paste_data['expiry'] is not None and datetime.now() > paste_data['expiry']:
                del pastes[paste_id]
                return {"success": False, "error": "Paste expired"}, 404
            
            content = paste_data['content']
            return {"success": True, "data": content}        
        else:
            return {"success": False, "error": "Paste not found"}, 404

        

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/<paste_id>', methods=['GET'])
def view_paste(paste_id):
    return render_template("view_paste.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=('cert.pem', 'key.pem'))
