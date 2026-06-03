from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

from routes.chat import chat_bp
from routes.index import index_bp
from routes.summarize import summarize_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(chat_bp)
app.register_blueprint(index_bp)
app.register_blueprint(summarize_bp)

@app.route('/')
def home():
    return {'message': 'AI Service running', 'status': 'success'}

if __name__ == '__main__':
    port = int(os.getenv('PORT', 7860))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)