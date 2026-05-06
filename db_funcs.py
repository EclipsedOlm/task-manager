import psycopg2 # Database access library
from psycopg2.extras import RealDictCursor # Essentially row_factory of sqlite3
import os # To get environment variables

# PLEASE PLEASE PLEASE DON'T TOUCH THIS IT WORKS!!!
# Apparently connecting with IPv6 (which is what we all do apparently) only works with this "pooling"
# And DOES NOT work with Direct Connection (which uses IPv4 I think - we didn't pay for this)
link = "postgresql://postgres.lwolbogymjkydwumhepb:{}@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres".format(os.environ["PASSKEY"]) # Keeping passkeys secret!
conn = psycopg2.connect(link) # Connect to the Supabase database
cursor = conn.cursor(cursor_factory=RealDictCursor) # The cursor object is the one that executes the SQL code

# SOME RULES FOR EXECUTING SQL QUERIES (Supabase/psycopg2 stuff)
# When selecting from a table, use "table name" with double quotes to preserve case (postgreSQL nonsense)
# -> Hence all my table names are lowercase
# -> I think double quotes ALWAYS will cause it to think its a table name and throw errors
# When retrieving data, do a cursor.execute() and then print(cursor.fetchall()) later on
# FORMAT OF cursor.fetchall(): [RealDictRow, RealDictRow, ...]; note that RealDictRow can be converted to Dict using dict()

# Example of SQL Code:
# cursor.execute("INSERT INTO users(username, admin) VALUES (%s,%s)", ('Aqua', True))
# cursor.execute("SELECT * FROM users WHERE username = 'stop'")
# print(cursor.fetchall())

# Here lies the various functions that will be used
# Yes I'll define datatypes explicitly because industry-ready: @furinafufu will just call this later

# To all the future people reading this, apologies for how repetitive some code may seem
# I'm sure I could cut down 100 lines with better modularisation
# But doing that ain't gonna net me 1 more mark here (or in computing TPs for that matter) ~
# Perhaps for another project!


def retrieveUser(username: str):
    # Retrieve all users with the same name (should either be len 0 or 1 array returned)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    return cursor.fetchall()


def insertUser(username: str, password: str, admin: bool):
    if len(username) > 30 or len(password) > 30:
        return "max_length_reached"

    if len(retrieveUser(username)) == 0:
        is_admin = True if username == "admin" else admin

        cursor.execute(
            "INSERT INTO users(username, password, admin) VALUES (%s,%s,%s)",
            (username, password, is_admin)
        )
        conn.commit()
        return "success"

    return "name_conflict"


def retrieveGroup(group_name: str):
    # Retrieve all groups with the same name (should either be len 0 or 1 array returned)
    cursor.execute("SELECT * FROM groups WHERE group_name = %s", (group_name,))
    return cursor.fetchall()


def insertGroup(group_name: str, group_desc: str, group_icon: str, group_password: str):
    if(len(retrieveGroup(group_name)) == 0):
        cursor.execute("INSERT INTO groups(group_name, group_description, group_icon, group_password) VALUES (%s,%s,%s,%s)", (group_name, group_desc, group_icon, group_password))
        conn.commit()
        return "success"
    else:
        # There is a group with the same name!
        return "name_conflict"
    

def addUserToGroup(username, group_name):
    # Get user data
    user_data = retrieveUser(username)
    if len(user_data) == 0:
        return "user_not_found"

    # Get group data
    group_data = retrieveGroup(group_name)
    if len(group_data) == 0:
        return "group_not_found"

    user_id = dict(user_data[0])["user_id"]
    group_id = dict(group_data[0])["group_id"]

    # Prevent duplicate membership
    cursor.execute(
        "SELECT * FROM users_groups WHERE user_id = %s AND group_id = %s",
        (user_id, group_id)
    )

    if len(cursor.fetchall()) > 0:
        return "already_in_group"

    cursor.execute(
        "INSERT INTO users_groups(user_id, group_id) VALUES (%s, %s)",
        (user_id, group_id)
    )

    conn.commit()
    return "success"


def retrieveGroupsForUser(username: str):
    user_data = retrieveUser(username)
    if len(user_data) == 0:
        return []
    user_id = dict(user_data[0])['user_id']

    cursor.execute("""SELECT groups.* 
                      FROM groups INNER JOIN users_groups 
                      ON groups.group_id = users_groups.group_id
                      WHERE users_groups.user_id = %s""", (user_id,))
    return cursor.fetchall()


def retrieveAllGroups():
    cursor.execute("SELECT * FROM groups")
    return cursor.fetchall()


def retrieveMembersByGroup(group_name: str):
    group_data = retrieveGroup(group_name)
    if(len(group_data) == 0):
        return []
    group_id = dict(group_data[0])["group_id"]

    cursor.execute("""SELECT users.username 
                      FROM users INNER JOIN users_groups
                      ON users.user_id = users_groups.user_id
                      WHERE users_groups.group_id = %s""", (group_id,))
    return cursor.fetchall()


def deleteGroup(group_name):
    group_data = retrieveGroup(group_name)
    if(len(group_data) == 0):
        return "group_not_found"
    
    cursor.execute("DELETE FROM groups WHERE group_name = %s", (group_name,))
    conn.commit()
    return "success"


def retrieveTasksForUser(username: str):
    user_data = retrieveUser(username)

    if len(user_data) == 0:
        return []

    user_id = dict(user_data[0])["user_id"]

    cursor.execute("""
        SELECT
            tasks.task_id,
            tasks.task_name AS title,
            tasks.task_description AS description,
            assigned_user.username AS assigned_to,
            created_user.username AS created_by,
            tasks.status,
            tasks.priority,
            tasks.deadline,
            tasks.icon,
            groups.group_name
        FROM tasks
        INNER JOIN groups
            ON tasks.group_id = groups.group_id
        INNER JOIN users_groups
            ON groups.group_id = users_groups.group_id
        INNER JOIN users AS assigned_user
            ON tasks.user_assigned_id = assigned_user.user_id
        INNER JOIN users AS created_user
            ON tasks.user_created_id = created_user.user_id
        WHERE users_groups.user_id = %s
        ORDER BY tasks.deadline ASC NULLS LAST, tasks.task_id DESC
    """, (user_id,))

    return cursor.fetchall()


def getTaskInfo(task_id: int):
    cursor.execute("""
        SELECT
            tasks.task_id,
            tasks.task_name AS title,
            tasks.task_description AS description,
            assigned_user.username AS assigned_to,
            created_user.username AS created_by,
            tasks.status,
            tasks.priority,
            tasks.deadline,
            tasks.icon,
            groups.group_name
        FROM tasks
        INNER JOIN groups
            ON tasks.group_id = groups.group_id
        INNER JOIN users AS assigned_user
            ON tasks.user_assigned_id = assigned_user.user_id
        INNER JOIN users AS created_user
            ON tasks.user_created_id = created_user.user_id
        WHERE tasks.task_id = %s
    """, (task_id,))

    return cursor.fetchall()


def insertTask(title: str, description: str, assigned_to: str, created_by: str, status: str, priority: str, deadline: str, icon: str, group_name: str):

    create_user = retrieveUser(created_by)
    if len(create_user) == 0:
        return "create_user_not_found"

    assign_user = retrieveUser(assigned_to)
    if len(assign_user) == 0:
        return "assign_user_not_found"

    group_data = retrieveGroup(group_name)
    if len(group_data) == 0:
        return "group_not_found"

    create_user_id = dict(create_user[0])["user_id"]
    assign_user_id = dict(assign_user[0])["user_id"]
    group_id = dict(group_data[0])["group_id"]

    cursor.execute("""
        INSERT INTO tasks
        (user_created_id, user_assigned_id, group_id, task_name, task_description, status, priority, deadline, icon)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        create_user_id,
        assign_user_id,
        group_id,
        title,
        description,
        status,
        priority,
        deadline,
        icon
    ))

    conn.commit()
    return "success"

#this version should just work
def deleteTask(task_id: int):
    cursor.execute("SELECT * FROM tasks WHERE task_id = %s", (task_id,))
    tasks = cursor.fetchall()

    if len(tasks) == 0:
        return "task_not_found"

    cursor.execute("DELETE FROM tasks WHERE task_id = %s", (task_id,))
    conn.commit()
    return "success"

#Some clean ups
def editTask(task_id: int, title: str, description: str, assigned_to: str, created_by: str, status: str, priority: str, deadline: str, icon: str):

    task_data = getTaskInfo(task_id)
    if len(task_data) == 0:
        return "task_not_found"
    task = dict(task_data[0])

    # Only creator can edit
    if task["created_by"] != created_by:
        return "user_no_perms"
    create_user = retrieveUser(created_by)
    if len(create_user) == 0:
        return "create_user_not_found"
    assign_user = retrieveUser(assigned_to)
    if len(assign_user) == 0:
        return "assign_user_not_found"
    create_user_id = dict(create_user[0])["user_id"]
    assign_user_id = dict(assign_user[0])["user_id"]

    cursor.execute("""
        UPDATE tasks
        SET
            user_created_id = %s,
            user_assigned_id = %s,
            task_name = %s,
            task_description = %s,
            status = %s,
            priority = %s,
            deadline = %s,
            icon = %s
        WHERE task_id = %s
    """, (
        create_user_id,
        assign_user_id,
        title,
        description,
        status,
        priority,
        deadline,
        icon,
        task_id
    ))

    conn.commit()
    return "success"


def updateTaskStatus(task_id: str, status: str):
    cursor.execute("SELECT * FROM tasks WHERE task_id = %s", (task_id,))
    tasks = cursor.fetchall()
    if(len(tasks) == 0):
        return "task_not_found"
    cursor.execute("UPDATE tasks SET status= %s WHERE task_id = %s", (status, task_id))
    conn.commit()
    return "success"


def updateProfilePicture(username: str, profile_picture: str):
    user_data = retrieveUser(username)
    if len(user_data) == 0:
        return "user_not_found"
    cursor.execute(
        "UPDATE users SET profile_picture = %s WHERE username = %s",
        (profile_picture, username)
    )
    conn.commit()
    return "success"


def getProfilePicture(username: str):
    user_data = retrieveUser(username)
    if len(user_data) == 0:
        return "None"
    cursor.execute(
        "SELECT profile_picture FROM users WHERE username = %s",(username,))
    result = cursor.fetchall()
    if len(result) == 0:
        return "None"
    profile_picture = dict(result[0]).get("profile_picture")
    if profile_picture is None or profile_picture == "":
        return "None"
    return profile_picture


def sendMessage(username: str, message: str):
    if len(message.strip()) == 0:
        return "empty_message"
    
    # This isn't the best strategy (honestly should've been seconds since 2000 or smth like that) but...
    # There is a row in the table that is {index: 0, username: NEXT_INDEX, message: (next index)}
    # where (next_index) is the next free index for the next message
    cursor.execute(
        "SELECT message FROM messages WHERE username = %s",("NEXT_INDEX",))
    result = cursor.fetchall()
    if len(result) == 0:
        next_index = 1
        cursor.execute('INSERT INTO messages("index", username, message) VALUES (%s, %s, %s)',(0, "NEXT_INDEX", str(next_index)))
    else:
        next_index = int(dict(result[0])["message"])
    cursor.execute(
        'INSERT INTO messages("index", username, message) VALUES (%s, %s, %s)',(next_index, username, message))
    cursor.execute(
        "UPDATE messages SET message = %s WHERE username = %s",(str(next_index + 1), "NEXT_INDEX"))
    conn.commit()
    return "success"


def getChatHistory():
    cursor.execute("""
        SELECT
            messages.username,
            messages.message,
            COALESCE(users.profile_picture, 'None') AS profile_picture
        FROM messages
        LEFT JOIN users
            ON messages.username = users.username
        WHERE messages.username <> %s
        ORDER BY messages."index" ASC
    """, ("NEXT_INDEX",))
    return cursor.fetchall()

def removeUserFromGroup(username: str, group_name: str):
    user_data = retrieveUser(username)
    if len(user_data) == 0:
        return "user_not_found"

    group_data = retrieveGroup(group_name)
    if len(group_data) == 0:
        return "group_not_found"

    user_id = dict(user_data[0])["user_id"]
    group_id = dict(group_data[0])["group_id"]

    cursor.execute(
        "DELETE FROM users_groups WHERE user_id = %s AND group_id = %s",
        (user_id, group_id)
    )

    if cursor.rowcount == 0:
        conn.commit()
        return "not_in_group"

    # If this was the last member, clean up the empty troupe too.
    cursor.execute(
        "SELECT COUNT(*) AS member_count FROM users_groups WHERE group_id = %s",
        (group_id,)
    )
    member_count = dict(cursor.fetchall()[0])["member_count"]

    if member_count == 0:
        # Remove tasks in the empty troupe first so foreign key links do not block deletion.
        cursor.execute("DELETE FROM tasks WHERE group_id = %s", (group_id,))
        cursor.execute("DELETE FROM groups WHERE group_id = %s", (group_id,))

    conn.commit()
    return "success"