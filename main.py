# Imports: 
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash # Flask functionality
from db_funcs import * # Database functionality

app = Flask(__name__) # Create the Flask app
app.secret_key = "temporary_secret_key"

#Ikik it's hardcoded but GIMME A BREAK ITS 3AM
#If you feel like it you can add a folder search and check ig
pfp_list = [
    "None",
    "Furina_smiling.png",
    "Furina_directing.png",
    "Furina_teatime.png",

    "furina_icon_1.jpg",
    "furina_icon_2.jpg",
    "furina_icon_3.webp",
    "furina_icon_4.jpg",
    "furina_icon_5.png",
    "furina_icon_6.png",
    "furina_icon_7.png",
    "furina_icon_8.png",
    "furina_icon_9.png",
    "furina_icon_10.png",
    "furina_icon_11.jpg",
    "furina_icon_12.png",
    "furina_icon_13.png",
    "furina_icon_14.png",
    "furina_icon_15.png",
    "furina_icon_16.png",
    "furina_icon_17.png",
    "furina_icon_18.webp",
    "furina_icon_19.png",
    "furina_icon_20.png",
    "furina_icon_21.png",
    "furina_icon_22.png",
    "furina_icon_23.png",
    "furina_icon_24.png",
    "furina_icon_25.png",
    "furina_icon_26.png",
    "furina_icon_27.png",
    "furina_icon_28.png",
]

#This is an empty check to prevent crashes (there're prob better ways but im too lazy)
def to_list(data):
    if data is None:
        return []

    # If a db function returns an error string like "user_not_found"
    if isinstance(data, str):
        return []

    return data

#I'm paranoid lel
def check_profile_picture(profile_data):
    try:
      if profile_data is None:
          return "None"
      if isinstance(profile_data, str) and profile_data in pfp_list:
          return profile_data if profile_data else "None"
      else:
          return None
    except Exception:
        return "None"

def get_value(row, key, default=None):
    if row is None:
        return default
    try:
        return dict(row).get(key, default)
    except Exception:
        return default



# Main homepage
@app.route("/", methods=["GET", "POST"])
def redir():
    return redirect(url_for("home")) #this just redirects just leave it


@app.route("/home", methods=["GET", "POST"])
def home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    username = session["username"]

    #trying to get all the db info here
    user_data = retrieveUser(username)
    user_groups = to_list(retrieveGroupsForUser(username))
    all_groups = to_list(retrieveAllGroups())
    tasks = to_list(retrieveTasksForUser(username))
    chat_history = to_list(getChatHistory())
    profile_picture = check_profile_picture(getProfilePicture(username))
    reset_furina_viewport = session.pop("reset_furina_viewport", False)

    members_by_group = {}

    for group in user_groups:
        group_name = get_value(group, "group_name")

        if group_name is not None:
            members_by_group[group_name] = to_list(retrieveMembersByGroup(group_name))

    #Send all these info to the html file
    return render_template(
        "newindex.html",
        username=username,
        user_data=user_data,
        user_groups=user_groups,
        all_groups=all_groups,
        tasks=tasks,
        chat_history=chat_history,
        profile_picture=profile_picture,
        reset_furina_viewport=reset_furina_viewport,
        members_by_group=members_by_group
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_data = retrieveUser(username)
        if(len(user_data) == 0):
            # Logic for user not found
            return render_template(
                "login.html",
                auth_error="Furina doesn't recognize this password/username",
                auth_image="furina_pw_wrong.png"
            )
        else:
            # There should only be 1 record since usernames are unique in the db
            if(password == dict(user_data[0])["password"]):
                # Logic for correct password and username
                session["logged_in"] = True
                session["username"] = username
                session["reset_furina_viewport"] = True
                flash("Welcome back to the stage!", "success")
                return redirect(url_for("home"))
            else:
                # Logic for wrong password
                return render_template(
                    "login.html",
                    auth_error="Furina doesn't recognize this password/username",
                    auth_image="furina_pw_wrong.png"
                )
    
    return render_template("login.html")


#I think this is fine (To get in just put "admin" in register username and anything in passwords)
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        result = insertUser(username, password, False)

        if result == "success":
            session["logged_in"] = True
            session["username"] = username
            session["reset_furina_viewport"] = True
            flash("Account created. Welcome to the troupe!", "success")
            return redirect(url_for("home"))
        else:
            return render_template(
                "register.html",
                error="Username already exists.",
                auth_error="Furina already knows someone with this name...",
                auth_image="furina_user_exist.png"
            )

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

#These are gonna be the functions (hopeful sth dont self-destruct)
@app.route("/create_troupe", methods=["POST"])
def create_troupe():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    username = session["username"]

    group_name = request.form["group_name"]
    group_desc = request.form.get("group_desc", "")
    group_icon = request.form.get("group_icon", "🎩")
    group_password = request.form.get("group_password", "")

    result = insertGroup(group_name, group_desc, group_icon, group_password)

    if result == "success":
        addUserToGroup(username, group_name)
        flash("Troupe successfully created!", "success")
    elif result == "name_conflict":
        flash("Furina already knows a troupe with this name.", "error")
    else:
        flash("Furina could not create this troupe.", "error")

    return redirect(url_for("home"))


@app.route("/join_troupe", methods=["POST"])
def join_troupe():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    username = session["username"]
    group_name = request.form["group_name"]
    group_password = request.form.get("group_password", "")

    group_data = retrieveGroup(group_name)

    if len(group_data) == 0:
        flash("Furina could not find this troupe.", "error")
        return redirect(url_for("home"))

    group = dict(group_data[0])

    if group_password == group.get("group_password", ""):
        result = addUserToGroup(username, group_name)

        if result == "success":
            flash("You joined the troupe successfully!", "success")
        elif result == "already_in_group":
            flash("You are already performing with this troupe.", "info")
        else:
            flash("Furina could not add you to this troupe.", "error")
    else:
        flash("Furina says the troupe password is wrong.", "error")

    return redirect(url_for("home"))


@app.route("/add_performance", methods=["POST"])
def add_performance():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    created_by = session["username"]

    group_name = request.form["group_name"]
    title = request.form["title"]
    description = request.form.get("description", "")
    assigned_to = request.form["assigned_to"]
    priority = request.form.get("priority", "Medium")
    deadline = request.form.get("deadline", "")
    icon = request.form.get("performance_icon", "🎼")
    status = request.form.get("status", "Not Started")

    result = insertTask(
        title,
        description,
        assigned_to,
        created_by,
        status,
        priority,
        deadline,
        icon,
        group_name
    )

    if result == "success":
        flash("Performance successfully created!", "success")
    else:
        flash("Furina could not create this performance.", "error")

    return redirect(url_for("home"))


@app.route("/delete_task/<task_id>", methods=["POST"])
def delete_task(task_id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    username = session["username"]

    try:
        task_data = getTaskInfo(task_id)

        if len(task_data) == 0:
            flash("Furina could not find this performance.", "error")
            return redirect(url_for("home"))

        task = dict(task_data[0])

        # Only creator can delete the task
        if task["created_by"] != username:
            flash("Only the creator can delete this performance.", "error")
            return redirect(url_for("home"))

        result = deleteTask(task_id)

        if result == "success":
            flash("Performance successfully deleted.", "success")
        else:
            flash("Furina could not delete this performance.", "error")

    except Exception as error:
        conn.rollback()
        print("delete_task failed:", error)
        flash("Something went wrong while deleting this performance.", "error")

    return redirect(url_for("home"))


@app.route("/edit_task/<task_id>", methods=["POST"])
def edit_task(task_id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    username = session["username"]

    try:
        task_data = getTaskInfo(task_id)

        if len(task_data) == 0:
            flash("Furina could not find this performance.", "error")
            return redirect(url_for("home"))

        task = dict(task_data[0])

        # Only the original creator is allowed to edit full task details
        if task["created_by"] != username:
            flash("Only the creator can edit the full performance details.", "error")
            return redirect(url_for("home"))

        title = request.form["title"]
        description = request.form.get("description", "")
        assigned_to = request.form["assigned_to"]
        status = request.form.get("status", "Not Started")
        priority = request.form.get("priority", "Medium")

        # If user clears the date input, keep old deadline instead of sending ""
        deadline = request.form.get("deadline") or task.get("deadline")

        icon = request.form.get("performance_icon", "🎼")

        result = editTask(
            task_id,
            title,
            description,
            assigned_to,
            task["created_by"],
            status,
            priority,
            deadline,
            icon
        )

        if result == "success":
            flash("Performance successfully edited!", "success")
        else:
            flash("Furina could not edit this performance.", "error")

    except Exception as error:
        conn.rollback()
        print("edit_task failed:", error)
        flash("Something went wrong while editing this performance.", "error")

    return redirect(url_for("home"))


@app.route("/update_task_status/<task_id>", methods=["POST"])
def update_task_status(task_id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    status = request.form.get("status", "Not Started")

    try:
        result = updateTaskStatus(task_id, status)

        if result == "success":
            flash("Performance status successfully updated!", "success")
        else:
            flash("Furina could not update this performance status.", "error")
    except Exception as error:
        conn.rollback()
        print("update_task_status failed:", error)
        flash("Something went wrong while updating the status.", "error")

    return redirect(url_for("home"))


@app.route("/update_profile_picture", methods=["POST"])
def update_profile_picture():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    username = session["username"]
    profile_picture = request.form.get("profile_picture", "None")

    result = updateProfilePicture(username, profile_picture)

    if result == "success":
        flash("Profile picture successfully changed!", "success")
    else:
        flash("Furina could not change your profile picture.", "error")

    return redirect(url_for("home"))


@app.route("/send_message", methods=["POST"])
def send_message():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    username = session["username"]
    message = request.form.get("message", "").strip()

    if message:
        sendMessage(username, message)

    return redirect(url_for("home"))


#this is for the dynamic drop down when you choose a group the members changes too (I hope at least) so we pass a .json for the javascript
@app.route("/members/<group_name>")
def members(group_name):
    if not session.get("logged_in"):
        return jsonify([])

    group_members = to_list(retrieveMembersByGroup(group_name))

    result = []

    for member in group_members:
        member_username = get_value(member, "username")

        if member_username is not None:
            result.append(member_username)

    return jsonify(result)


@app.route("/leave_troupe", methods=["POST"])
def leave_troupe():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    username = session["username"]
    group_name = request.form["group_name"]

    try:
        result = removeUserFromGroup(username, group_name)

        if result == "success":
            flash("You successfully left the troupe.", "success")
        else:
            flash("Furina could not remove you from this troupe.", "error")
    except Exception as error:
        conn.rollback()
        print("leave_troupe failed:", error)
        flash("Something went wrong while leaving this troupe.", "error")

    return redirect(url_for("home"))


if __name__ == "__main__":
  app.run(port=5000)
