import secrets
import sqlite3
import string
import sys
import yaml
from datetime import datetime, timedelta

from flask import Flask, request, render_template

app = Flask(__name__)

# Load the configuration from the YAML file
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

class Paste:
    def __init__(self, id=None, content=None, expiry=None):
        self.id = id or self.generate_random_id()
        self.content = content
        self.expiry = expiry or self.parse_expiry_time(config['paste']['default_expiry'])

    @staticmethod
    def generate_random_id(length=16):
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))

    @staticmethod
    def parse_expiry_time(expiry_option):
        if expiry_option == '1_minute':
            expiry_time = datetime.now() + timedelta(minutes=1)
        elif expiry_option == '5_minute':
            expiry_time = datetime.now() + timedelta(minutes=5)
        elif expiry_option == '10_minute':
            expiry_time = datetime.now() + timedelta(minutes=10)
        elif expiry_option == '1_hour':
            expiry_time = datetime.now() + timedelta(hours=1)
        elif expiry_option == '1_day':
            expiry_time = datetime.now() + timedelta(days=1)
        elif expiry_option is None:
            expiry_time = None
        else:
            expiry_time = datetime.now() + timedelta(days=1)
        return expiry_time

    @staticmethod
    def init_db():
        with sqlite3.connect(config['database']['name']) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS pastes
                         (id TEXT PRIMARY KEY, content TEXT NOT NULL, expiry TIMESTAMP NOT NULL)''')
            conn.commit()


class PasteAPI:
    @app.route('/api/v1/secure-paste', methods=['POST'])
    def secure_paste():
        if request.method == 'POST':
            if not 'data' in request.json:
                print('no data key')
                return {'success': False}, 400
            if sys.getsizeof(request.json['data'].encode('utf-8')) > config['paste']['max_size']:  # Limit paste size to 10MB in bytes
                return {'success': False, 'error': 'Paste too large'}, 400
            paste = Paste(content=request.json['data'], expiry=Paste.parse_expiry_time(request.json.get('expiry', config['paste']['default_expiry'])))

            with sqlite3.connect(config['database']['name']) as conn:
                c = conn.cursor()
                c.execute('INSERT INTO pastes (id, content, expiry) VALUES (?, ?, ?)',
                          (paste.id, paste.content, paste.expiry.strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()

            return {
                'success': True,
                'id': paste.id
            }

    @app.route('/api/v1/secure-paste/<paste_id>', methods=['GET'])
    def secure_paste2(paste_id):
        if request.method == 'GET':
            print(request.args)
            with sqlite3.connect('pastes.db') as conn:
                c = conn.cursor()
                c.execute('SELECT content, expiry FROM pastes WHERE id=?', (paste_id,))
                paste_data = c.fetchone()

                if paste_data:
                    content, expiry = paste_data
                    expiry_datetime = datetime.strptime(expiry, '%Y-%m-%d %H:%M:%S')

                    if expiry_datetime and datetime.now() > expiry_datetime:
                        c.execute('DELETE FROM pastes WHERE id=?', (paste_id,))
                        conn.commit()
                        return {'success': False, 'error': 'Paste expired'}, 404

                    return {'success': True, 'data': content}
                else:
                    return {'success': False, 'error': 'Paste not found'}, 404


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/<paste_id>', methods=['GET'])
def view_paste(paste_id):
    return render_template('view_paste.html')


if __name__ == '__main__':
    Paste.init_db()
    app.run(host=config['server']['host'], port=config['server']['port'], debug=config['server']['debug'])