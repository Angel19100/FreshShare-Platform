from flask import Flask, request, jsonify, render_template, redirect, url_for
from database import get_connection, initialize_database

app = Flask(__name__)

initialize_database()


@app.route("/")
def home():
    return render_template("index.html")


# ---------- PAGES ----------

@app.route("/register_page")
def register_page():
    return render_template("register.html")


@app.route("/add_food_page")
def add_food_page():
    return render_template("add_food.html")


# ---------- FORM ACTIONS ----------

@app.route("/register_form", methods=["POST"])
def register_form():
    name = request.form.get("name")
    role = request.form.get("role")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, role) VALUES (?, ?)", (name, role))
    conn.commit()
    conn.close()

    return redirect(url_for("home"))


@app.route("/add_food_form", methods=["POST"])
def add_food_form():
    name = request.form.get("name")
    quantity = request.form.get("quantity")
    donor_id = request.form.get("donor_id")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT role FROM users WHERE id=?", (donor_id,))
    user = cursor.fetchone()

    if not user or user[0] != "donor":
        conn.close()
        return "Only donors can add food"

    cursor.execute(
        "INSERT INTO food (name, quantity, status, donor_id) VALUES (?, ?, 'available', ?)",
        (name, quantity, donor_id)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


# ---------- API ----------

@app.route("/food")
def view_food():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT food.id, food.name, food.quantity, users.name
    FROM food
    JOIN users ON food.donor_id = users.id
    WHERE food.status='available'
    """)

    rows = cursor.fetchall()
    conn.close()

    food_list = []
    for row in rows:
        food_list.append({
            "id": row[0],
            "food_name": row[1],
            "quantity": row[2],
            "donor": row[3]
        })

    return jsonify(food_list)


@app.route("/claim/<int:food_id>", methods=["POST"])
def claim_food(food_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE food SET status='claimed' WHERE id=? AND status='available'",
        (food_id,)
    )

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"error": "Food already claimed"}), 400

    conn.commit()
    conn.close()

    return jsonify({"message": "Food claimed successfully"})


if __name__ == "__main__":
    app.run(debug=True)
