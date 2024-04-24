import flask
from flask import request, jsonify
import requests
import json
from data.giga_token import get_giga_token

blueprint = flask.Blueprint(
    'upload_images_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/upload_image', methods=['POST'])
def giga_chat():
    print(True)
    print(request.json)
