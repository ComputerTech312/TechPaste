from flask import Flask, request, render_template, url_for
from datetime import datetime, timedelta
import sys
import secrets
import string
import sqlite3

app = Flask(__name__)

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
    elif expiry_option is None:
        expiry_time = None
    else:
        expiry_time = datetime.now() + timedelta(days=1)
    return expiry_time

def init_db():
    with sqlite3.connect('pastes.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS pastes
                     (id TEXT PRIMARY KEY, content TEXT NOT NULL, expiry TIMESTAMP NOT NULL)''')
        conn.commit()

init_db()

@app.route("/api/v1/secure-paste", methods=["POST"])
def secure_paste():
    if request.method == "POST":
        if not "data" in request.json:
            print("no data key")
            return {"success": False}, 400
        if sys.getsizeof(request.json["data"].encode('utf-8')) > 10485760:  # Limit paste size to 10MB in bytes
            return {"success": False, "error": "Paste too large"}, 400
        id = generate_random_id()
        expiry_time = parse_expiry_time(request.json.get("expiry", "1_day"))

        with sqlite3.connect('pastes.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO pastes (id, content, expiry) VALUES (?, ?, ?)", 
                      (id, request.json["data"], expiry_time.strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
        
        return {
            "success": True,
            "id": id
        }
    
@app.route("/api/v1/secure-paste/<paste_id>", methods=["GET"])
def secure_paste2(paste_id):
    if request.method == "GET":
        print(request.args)
        with sqlite3.connect('pastes.db') as conn:
            c = conn.cursor()
            c.execute("SELECT content, expiry FROM pastes WHERE id=?", (paste_id,))
            paste_data = c.fetchone()

            if paste_data:
                content, expiry = paste_data
                expiry_datetime = datetime.strptime(expiry, '%Y-%m-%d %H:%M:%S')

                if expiry_datetime and datetime.now() > expiry_datetime:
                    c.execute("DELETE FROM pastes WHERE id=?", (paste_id,))
                    conn.commit()
                    return {"success": False, "error": "Paste expired"}, 404

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
#    if os.environ.get("DEBUG_NOSSL"):
        app.run(host='0.0.0.0', port=8888, debug=True)
    #else:
     #   app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=('cert.pem', 'key.pem'))
