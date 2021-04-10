from flask import Flask, request, jsonify

app = Flask(__name__, static_url_path='/', static_folder='../static')
