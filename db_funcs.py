import psycopg2 # Database access library
from psycopg2.extras import RealDictCursor # Essentially row_factory of sqlite3

# Put it into some secret variable later on
PASSKEY = "justiceforhina10" # POOR HINA I KNOW WHAT YOU FEEL

# PLEASE PLEASE PLEASE DON'T TOUCH THIS IT WORKS!!!
# Apparently connecting with IPv6 (which is what we all do apparently) only works with this "pooling"
# And DOES NOT work with Direct Connection (which uses IPv4 I think - we didn't pay for this)
link = "postgresql://postgres.lwolbogymjkydwumhepb:{}@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres".format(PASSKEY) # Keeping passkeys secret!
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


def retrieveUser(username: str):
    # Retrieve all users with the same name (should either be len 0 or 1 array returned)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    return cursor.fetchall()


def insertUser(username: str, password: str, admin: bool):
    if username == "admin":
        return "success"
    elif len(username) > 30 or len(password) > 30:
        return "max_length_reached"
    elif(len(retrieveUser(username)) == 0):
        cursor.execute("INSERT INTO users(username, password, admin) VALUES (%s,%s)", (username, password, admin))
        conn.commit()
        return "success"
    else:
        # There is a user with the same username!
        return "name_conflict"


def retrieveGroup(group_name: str):
    # Retrieve all groups with the same name (should either be len 0 or 1 array returned)
    cursor.execute("SELECT * FROM groups WHERE group_name = %s", (group_name,))
    return cursor.fetchall()


def insertGroup(group_name: str, group_desc: str):
    if(len(retrieveGroup(group_name)) == 0):
        cursor.execute("INSERT INTO groups(group_name, group_description) VALUES (%s,%s)", (group_name, group_desc))
        conn.commit()
        return "success"
    else:
        # There is a group with the same name!
        return "name_conflict"
    

def addUserToGroup(username, group_name):
    # Get user data
    user_data = retrieveUser(username)
    if(len(user_data) == 0):
        return "user_not_found"
    
    # Get group data
    group_data = retrieveGroup(group_name)
    if(len(group_data) == 0):
        return "group_not_found"
    
    # If both exist, then extract their IDs, and add new record in users_groups table
    user_id, group_id = dict(user_data[0])['user_id'], dict(group_data[0])['group_id']
    cursor.execute("INSERT INTO users_groups(user_id, group_id) VALUES (%s, %s)", (user_id, group_id))
    conn.commit()
    return "success"


# Some functions I plan to do in the future but idk if yall need. so lmk what functions yall need
# ESPECIALLy i need to know what info i will have, then i can make the relevant queries to get data to insert

#Wait let me help you out here I think these are the things I'd need for now and the info you get (with types)
def retrieveGroupsForUser(username:str):
    user_data = retrieveUser(username)

    #some magic happens here

    #return cursor.fetchall() then I get all the groups


def retrieveAllGroups():
    pass
    #Just dump lol select all or sth

    #return cursor.fetchall()


def retrieveMembersByGroup(group_name:str):
    group_data = retrieveGroup(group_name)

    #black magic happens here giving me all the members from the group

    #return cursor.fetchall()


def retrieveTasksForUser(username:str):
    user_data = retrieveUser(username)

    #gimme all the task of the user (wait lowkey i should put this behind insert task lol)

    #return cursor.fetchall()


def getTaskInfo(task_id: int):
    #get all the task info should be a one liner
    return cursor.fetchall()


def insertTask(title:str,description:str,assigned_to:str,created_by:str,status:str,priority:str,deadline:str,icon:str,group_name:str):
    group_data = retrieveGroup(group_name)

    #dump all these info into the db
    #VERY IMPORTANT YOU NEED A task_id COLUMN GENERATE IT HERE IF YOU WISH

    #conn.commit()
    #return "success"


def deleteTask(task_id:int):
    pass
    #delete
    #wait lowkey wouldn't it be cool if only the creator can delete the task

    #conn.commit()
    #return "success"


def editTask(task_id:int,title:str,description:str,assigned_to:str,created_by:str,status:str,priority:str,deadline:str,icon:str):
    pass
    #update the changes (only creator should be able to do this (actually we might have to check this in main.py))

    #conn.commit()
    #return "success"


def updateTaskStatus(task_id:int,status:str):
    pass
    #update changes to the status of the task (anyone can do this)

    #conn.commit()
    #return "success"

#Also ig we also need a delete group but it's not urgent ig we can just leave empty groups to die


def updateProfilePicture(username:str,profile_picture:str):
    user_data = retrieveUser(username)

    #update to db

    #conn.commit()
    #return "success"


def getProfilePicture(username:str):
    user_data = retrieveUser(username)

    #Get the pfp of the user (str)

    #return cursor.fetchall()


def sendMessage(username:str,message:str):
    user_data = retrieveUser(username)

    #add to db (I think we the db can be [Index][Username/ID][Message])
    #Index basically determines the orders of the messages so when we try to get the chat history we know the order

    #conn.commit()
    #return "success"


def getChatHistory():
    pass

    #Get the entire chat/msg db ig

    #return cursor.fetchall()