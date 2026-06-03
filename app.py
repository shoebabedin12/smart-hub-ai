from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
from fastapi import FastAPI

app = FastAPI()

load_dotenv()

from routes.chat import chat_bp
from routes.index import index_bp
from routes.summarize import summarize_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(chat_bp)
app.register_blueprint(index_bp)
app.register_blueprint(summarize_bp)
@app.get("/")
def greet_json():
    return {"Hello": "World!"}

@app.route('/')
def home():
    return {'message': 'AI Service running'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 6000)), debug=True, use_reloader=False)