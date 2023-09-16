from flask import Flask, request, render_template, url_for
from datetime import datetime, timedelta

app = Flask(__name__)

pastes = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        paste_content = request.form['content']
        expiry_option = request.form['expiry']
        paste_id = str(len(pastes) + 1)

        expiry_time = None
        if expiry_option == "1_minute":
            expiry_time = datetime.now() + timedelta(minutes=1)
        elif expiry_option == "1_hour":
            expiry_time = datetime.now() + timedelta(hours=1)

        pastes[paste_id] = {'content': paste_content, 'expiry': expiry_time}
        return render_template('paste_created.html', paste_id=paste_id, paste_url=url_for('view_paste', paste_id=paste_id, _external=True))

    return render_template('index.html')

@app.route('/<paste_id>', methods=['GET'])
def view_paste(paste_id):
    paste_data = pastes.get(paste_id)
    if paste_data is not None:
        if paste_data['expiry'] is not None and datetime.now() > paste_data['expiry']:
            del pastes[paste_id]
            return "Paste expired", 404
        
        content = paste_data['content']
        return render_template('view_paste.html', content=content)
    else:
        return "Paste not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=('cert.pem', 'key.pem'))
