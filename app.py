from flask import Flask, jsonify, request, render_template

app = Flask(__name__)
users = [
    {
        "id": "1",
        "name": "Stephen Murazik",
        "pNumber": "0225534438",
        "email": "stephenmurazik@gmail.com",
        "admin": False,
        "agent": False,
        "password": "StephenMurazik1!",
    },
    {
        "id": "2",
        "Name": "Sonya White",
        "pNumber": "0325534438",
        "email": "sonyawhite@gmail.com",
        "admin": True,
        "agent": False,
        "password": "SonyaWhite1!",
    },
    {
        "id": "3",
        "Name": "Ira Homenick",
        "pNumber": "0425534438",
        "email": "irahomenick@gmail.com",
        "admin": True,
        "agent": False,
        "password": "IraHomenick1!",
    },
    {
        "id": "4",
        "fName": "Shannon Zulauf",
        "pNumber": "0525534438",
        "email": "shannonzulaf@gmail.com",
        "admin": False,
        "agent": False,
        "password": "ShannonZulaf1!",
    },
]

policies = [
    {
        "policy_id": "1",
        "policy_type": "Vehicle",
        "coverage": "comprehensive",
        "img": "https://www.jamesedition.com/stories/wp-content/uploads/2022/11/16-630x420.jpg",
    },
    {
        "policy_id": "2",
        "policy_type": "Vehicle",
        "coverage": "Third-Party, Fire and Theft",
        "img": "https://i.kinja-img.com/image/upload/c_fill,h_675,pg_1,q_80,w_1200/1a34b102a47ef5e84bcd8dc73359f44c.jpg",
    },
    {
        "policy_id": "3",
        "policy_type": "Vehicle",
        "coverage": "Third-Party",
        "img": "https://blog.suzukiauto.co.za/hubfs/Swift%20MC%202021/Suzuki%20Swift%202021%20-%20160%20_%20Resized-1.png#keepProtocol",
    },
]

policyholder = [
    {
        "policyholder_id": "1",
        "user_id": "1",
        "policy_id": "3",
        "start_date": "2024-03-17",
        "id_number": 1234567891012,
        "address": "124 school str Claremont",
    },
    {
        "policyholder_id": "4",
        "user_id": "4",
        "policy_id": "1",
        "start_date": "2024-03-17",
        "id_number": 1234567891015,
        "address": "85 Marlin Close Fish Hoek",
    },
]


@app.route("/")
def home():
    return render_template("home.html", policies=policies)


@app.route("/policy_details")
def policy_details(id):
    policy = next((policy for policy in policies if policy["id"] == id), None)
    if policy:
        return render_template("policy_detail.html", policy=policy)
    else:
        return "Policy not found", 404


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/profile")
def profile():
    return render_template("profile.html", users=users)


@app.route("/comprehensive")
def comprehensive():
    filtered_policy = None
    for policy in policies:
        if policy["policy_id"] == "1":
            filtered_policy = policy
            break
    return render_template("comprehensive.html", policy=filtered_policy)


@app.route("/third_party")
def third_party():
    filtered_policy = None
    for policy in policies:
        if policy["policy_id"] == "3":
            filtered_policy = policy
            break
    return render_template("third_party.html", policy=filtered_policy)


@app.route("/fire_theft")
def fire_theft():
    filtered_policy = None
    for policy in policies:
        if policy["policy_id"] == "2":
            filtered_policy = policy
            break
    return render_template("fire_theft.html", policy=filtered_policy)


# USERS CRUD OPERATIONS
# GET users
@app.get("/users")
def get_users():
    return jsonify(users)


# GET user by id
@app.get("/users/<id>")
def get_users_by_id(id):
    filtered_user = next((user for user in users if user["id"] == id), None)
    if filtered_user:
        return jsonify(filtered_user)
    else:
        return jsonify({"message": "User not found"}), 404


# DELETE user by id
@app.delete("/users/<id>")
def delete_user(id):
    deleted_user = next((user for user in users if user["id"] == id), None)
    if deleted_user:
        users.remove(deleted_user)
        return jsonify({"message": "Movie deleted sucessfully", "data": deleted_user})
    else:
        return jsonify({"message": "Movie not found"}), 404


# Update a user
@app.put("/users/<id>")
def update_user_by_id(id):
    data = request.json

    user_to_update = next((user for user in users if user["id"] == id), None)
    if user_to_update:
        user_to_update.update(data)
        return jsonify({"message": "Movie updated", "data": user_to_update})
    else:
        return jsonify({"message": "Movie not updated"}), 404


# Register a user
@app.route("/register", methods=["GET"])
def register_user_form():
    return render_template("register.html")


@app.route("/home", methods=["POST"])
def register_user():
    user_ids = [int(user["id"]) for user in users]
    max_id = max(user_ids)
    next_id = str(max_id + 1)

    name = request.form["name"]
    number = request.form["number"]
    email = request.form["email"]
    password = request.form["password"]

    new_user = {
        "id": next_id,
        "name": name,
        "number": number,
        "email": email,
        "password": password,
    }
    users.append(new_user)

    return jsonify({"success": True})


# User login
@app.route("/login", methods=["GET"])
def signin_form():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_user():
    email = request.form.get("email")
    password = request.form.get("password")

    for user in users:
        if user["email"] == email and user["password"] == password:
            return jsonify(
                {"success": True, "message": "Login successful", "user": user}
            )

    return jsonify({"success": False, "message": "Invalid email or password"})


# Password reset form
@app.route("/reset_password", methods=["GET"])
def reset_password_form():
    return render_template("reset_password.html")


@app.route("/reset_password", methods=["POST"])
def reset_password():
    email = request.form.get("email")
    new_password = request.form.get("new_password")

    for user in users:
        if user["email"] == email:
            user["password"] = new_password
            return jsonify({"success": True, "message": "Password reset successfully."})

    return jsonify(
        {"success": False, "message": "User with this email does not exist."}
    )


# POLICY CRUD OPERATIONS
