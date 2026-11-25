from flask import Flask, request, Response
import os
import secrets
import html
import psycopg

app = Flask(__name__)

def authorized():
    auth = request.authorization
    if not auth:
        return False

    return (
        secrets.compare_digest(
            auth.username or "",
            os.environ.get("APP_USER", "")
        )
        and secrets.compare_digest(
            auth.password or "",
            os.environ.get("APP_PASSWORD", "")
        )
    )

@app.before_request
def check_access():
    if not authorized():
        return Response(
            "Login required",
            401,
            {"WWW-Authenticate": 'Basic realm="Training Lab"'}
        )

def connect_db():
    return psycopg.connect(os.environ["DATABASE_URL"])

@app.route("/")
def home():
    return Response(
        "<h2>Cyber Training Lab</h2>"
        "<p><a href='/training'>Open training demo</a></p>",
        mimetype="text/html"
    )

@app.route("/training")
def training():
    return """
    <h2>TRAINING SIMULATION</h2>
    <p>Not Instagram. Use dummy details only.</p>

    <form id="demo">
      <input id="username"
        placeholder="Dummy username" required>
      <br><br>
      <input id="password" type="password"
        placeholder="Demo password" required>
      <br><br>
      <button>Submit demo</button>
    </form>

    <p id="result"></p>

    <script>
    document.getElementById("demo").onsubmit =
    async function(e) {
      e.preventDefault();

      const username =
        document.getElementById("username").value;

      const matched =
        document.getElementById("password").value
        === "demo123";

      const response = await fetch("/training-submit", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          username: username,
          password_match: matched
        })
      });

      document.getElementById("result").innerText =
        response.ok
        ? "Demo submitted. Password was not sent."
        : "Submission failed.";
    };
    </script>
    """

@app.route("/training-submit", methods=["POST"])
def training_submit():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", ""))[:50]
    matched = data.get("password_match") is True

    if not username:
        return {"error": "Username required"}, 400

    message = (
        f"Training user: {html.escape(username)} | "
        f"Demo password matched: {matched}"
    )

    with connect_db() as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS messages "
            "(id SERIAL PRIMARY KEY, message TEXT NOT NULL)"
        )
        db.execute(
            "INSERT INTO messages (message) VALUES (%s)",
            (message,)
        )

    return {"status": "success"}
