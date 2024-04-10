import secrets
import sqlite3
import string
import sys
import yaml
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

from flask import Flask, request, render_template

app = Flask(__name__)

try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    print("config.yaml not found.")
    sys.exit(1)
except yaml.YAMLError as e:
    print(f"Error parsing config.yaml: {e}")
    sys.exit(1)


class Paste:
    def __init__(self, id=None, content=None, expiry=None):
        self.id = id or self.generate_random_id()
        self.content = content
        self.expiry = expiry or self.parse_expiry_time(
            config['paste']['default_expiry'])

    @staticmethod
    def generate_random_id(length=16):
        try:
            if not isinstance(length, int) or length <= 0:
                raise ValueError("Length must be a positive integer")

            characters = string.ascii_letters + string.digits
            return ''.join(secrets.choice(characters) for _ in range(length))
        except Exception as e:
            print(f"Error generating random id: {str(e)}")

    @staticmethod
    def generate_secret_key():
        return Fernet.generate_key().decode()

    @staticmethod
    def parse_expiry_time(expiry_option):
        try:
            expiry_options = {
                '1_minute': timedelta(minutes=1),
                '5_minute': timedelta(minutes=5),
                '10_minute': timedelta(minutes=10),
                '1_hour': timedelta(hours=1),
                '1_day': timedelta(days=1),
                None: None
            }

            if expiry_option not in expiry_options:
                raise ValueError(f"Invalid expiry option: {expiry_option}")

            expiry_time = datetime.now() + expiry_options[expiry_option] if expiry_option else None
        except Exception as e:
            print(f"Error parsing expiry time: {str(e)}")
            raise

        return expiry_time

    @staticmethod
    def init_db():
        conn = None
        try:
            conn = sqlite3.connect(config['database']['name'])
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS pastes
                         (id TEXT PRIMARY KEY, content TEXT NOT NULL, expiry TIMESTAMP NOT NULL)''')
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error initializing database: {str(e)}")
            sys.exit(1)
        finally:
            if conn:
                conn.close()


@app.route('/api/v1/generate_secret', methods=['GET'])
def generate_secret():
    try:
        secret_key = Paste.generate_secret_key()
        return {'success': True, 'secret_key': secret_key}
    except Exception as e:
        return {'success': False, 'error': 'Error generating secret key: ' + str(e)}, 500


class PasteAPI:
    @app.route('/api/v1/secure-paste', methods=['POST'])
    def secure_paste():
        if request.method == 'POST':
            if 'data' not in request.json:
                print('no data key')
                return {'success': False, 'error': 'No data key in request'}, 400
            if sys.getsizeof(request.json['data'].encode('utf-8')) > config['paste']['max_size']:
                return {'success': False, 'error': 'Paste too large'}, 400
            try:
                paste = Paste(content=request.json['data'],
                              expiry=Paste.parse_expiry_time(request.json.get('expiry', config['paste']['default_expiry'])))
            except Exception as e:
                return {'success': False, 'error': 'Error creating paste: ' + str(e)}, 500

            conn = None
            try:
                conn = sqlite3.connect(config['database']['name'])
                c = conn.cursor()
                c.execute('INSERT INTO pastes (id, content, expiry) VALUES (?, ?, ?)',
                          (paste.id, paste.content, paste.expiry.strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
            except sqlite3.Error as e:
                return {'success': False, 'error': 'Database error: ' + str(e)}, 500
            finally:
                if conn:
                    conn.close()

            return {
                'success': True,
                'id': paste.id
            }

    @app.route('/api/v1/secure-paste/<paste_id>', methods=['GET'])
    def secure_paste2(paste_id):
        if request.method == 'GET':
            conn = None
            try:
                conn = sqlite3.connect('pastes.db')
                c = conn.cursor()
                c.execute('SELECT content, expiry FROM pastes WHERE id=?', (paste_id,))
                paste_data = c.fetchone()
            except sqlite3.Error as e:
                return {'success': False, 'error': 'Database error: ' + str(e)}, 500
            finally:
                if conn:
                    conn.close()

            if paste_data:
                content, expiry = paste_data
                try:
                    expiry_datetime = datetime.strptime(expiry, '%Y-%m-%d %H:%M:%S')
                except ValueError as e:
                    return {'success': False, 'error': 'Invalid expiry date format: ' + str(e)}, 500

                if expiry_datetime and datetime.now() > expiry_datetime:
                    conn = None
                    try:
                        conn = sqlite3.connect('pastes.db')
                        c = conn.cursor()
                        c.execute('DELETE FROM pastes WHERE id=?', (paste_id,))
                        conn.commit()
                    except sqlite3.Error as e:
                        return {'success': False, 'error': 'Database error: ' + str(e)}, 500
                    finally:
                        if conn:
                            conn.close()

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
    try:
        Paste.init_db()
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)

    try:
        app.run(host=config['server']['host'], port=config['server']['port'], debug=config['server']['debug'])
    except Exception as e:
        print(f"Error running the Flask app: {e}")
        sys.exit(1)
