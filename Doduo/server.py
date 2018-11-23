"""
Doduo/Doduo.server

The Flask server for accessing a Doduo Matcher.
"""

from flask import request, jsonify, Flask
from flask_cors import CORS

from Doduo.matcher import Matcher
from Doduo.config import CONFIG_FILE
from Doduo import InvalidUsage


app = Flask(__name__)
cors = CORS(app)

# Instantiate the Matcher singleton. Blueprints in CONFIG_FILE
# will be compiled in this line.
main_matcher = Matcher(CONFIG_FILE)


@app.route("/match", methods=["POST"])
def api_match():
    """
    The main API endpoint to handle client requests for
    parsing query strings.
    """

    # `query` is a mandatory attribute.
    if "query" not in request.json:
        raise InvalidUsage("Request missing query.", status_code=400)
    query = request.json["query"]

    # `templates` is an optional attribute.
    if "templates" in request.json:
        template_ids = request.json["templates"]
    else:
        template_ids = None

    return jsonify(
        {
            "success": True,
            "matches": list(main_matcher.match(query, template_ids)),
        }
    )


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """
    Handle exceptions generated from invalid API usage and
    ensure it is handled smoothly.
    """
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == "__main__":
    print("Server running at localhost:5000")
    app.run(host="0.0.0.0", port=5000)
