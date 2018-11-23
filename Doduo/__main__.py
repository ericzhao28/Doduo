"""
Doduo/Doduo

Bring up the Doduo Flask API by calling `python3.6 -m Doduo`.
"""

from Doduo.server import app


if __name__ == "__main__":
    print("Server running at localhost:5000")
    app.run(host="0.0.0.0", port=5000)
