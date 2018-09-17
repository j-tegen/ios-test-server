from flask import jsonify

def make_response(status_code, status, message=None, data=None):
    response_content = dict(message=message, data=data, status=status)
    response = jsonify(
        {k: v for k, v in response_content.items() if v is not None})
    response.status_code = status_code
    return response
