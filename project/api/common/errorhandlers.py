from flask import jsonify
from ... import app


@app.errorhandler(422)
def handle_unprocessable_entity(err):
    # webargs attaches additional metadata to the `data` attribute
    exc = getattr(err, 'exc')
    print("!!!!!!!!!!!!!")
    if exc:
        # Get validations from the ValidationError object
        messages = exc.messages
    else:
        messages = ['Invalid request']
    return jsonify({
        'messages': messages,
    }), 422
