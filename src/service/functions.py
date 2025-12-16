import sqlite3 as sl
import json
import os
import shutil
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlparse
from config import Settings
import requests

data = os.environ.get("DATA_DIR", Settings.local_data)

def createDataFolder():
    #data = 'data/'
    if not os.path.exists(data):
        os.makedirs(data)
    return True

def uri_validator(x):
    try:
        result = requests.head(x)
        return result.status_code
    except:
        return 0

def createDataStoriesDB():
    #data = 'data'
    # if not os.path.exists(data):
    #     os.makedirs(data)

    con = sl.connect(data + '/datastories.db')
    cur = con.cursor()   
    cur.execute("""
            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                uuid TEXT,
                status TEXT DEFAULT 'draft',
                owner TEXT,
                filename TEXT,
                created TEXT,
                modified TEXT,
                store TEXT,
                title TEXT
            );
        """) 
    con.commit()
    cur.close()
    con.close()

def get_setting_users(uuid, eppn):
    sql = "select v.email, v.eppn from visitors v where v.eppn not in (select r.eppn from rights r where story_uuid = ?) and v.eppn is not ? order by email"
    values = (uuid, eppn)
    result = fetch_data(sql, values)
    return result

def fetch_data(sql, values):
    #data = 'data'
    con = sl.connect(data + '/datastories.db')
    cur = con.cursor()
    cur.execute(sql, values)
    names = list(map(lambda x: x[0], cur.description)) # ergens opgezocht
    #print(names)
    result = cur.fetchall()
    cur.close()
    con.close()
    #print(result)

    struct = []
    for x in result:
        row = {}
        # namen in het resultaat plakken y is een rangnummer in de namenlijst
        for y in range(0, len(names)):
            key = names[y]
            value = x[y]
            row[key] = value
            # s.append({key: value})

        struct.append(row)
    return struct

def change_data(sql, values):
    #data = 'data'
    con = sl.connect(data + '/datastories.db')
    cur = con.cursor()
    cur.execute(sql, values)
    con.commit()
    cur.close()
    con.close()
    return {"status": "OK"}

def save_user_rights_str(uuid, eppn, code):
    sql = "UPDATE rights SET rights = ? WHERE story_uuid = ? AND eppn = ?"
    values = (code, uuid, eppn)
    return change_data(sql, values)

def getDataStorySettings(id):
    #data = 'data'
    con = sl.connect(data + '/datastories.db')
    cur = con.cursor()
    sql = "SELECT status, title, uuid FROM stories WHERE uuid = '" + id + "'"
    cur.execute(sql)
    names = list(map(lambda x: x[0], cur.description)) # ergens opgezocht
    result = cur.fetchall()
    cur.close()
    con.close()

    struct = []
    for x in result:
        row = {}
    # namen in het resultaat plakken y is een rangnummer in de namenlijst
        for y in range(0, len(names)):
            key = names[y]
            value = x[y]
            row[key] = value
        # s.append({key: value})

        struct.append(row)
    struct[0]["rights"] = getStoryRights(id)
    return struct[0]

def add_user_rights(uuid, eppn):
    sql = "INSERT INTO rights (story_uuid, eppn, rights) VALUES (?, ?, ?)"
    values = (uuid, eppn, 'R----')
    result = change_data(sql, values)
    return result;

def revoke_user_rights(uuid, eppn):
    sql = "DELETE FROM rights WHERE story_uuid = ? AND eppn = ?"
    values = (uuid, eppn)
    result = change_data(sql, values)
    return result;

def getStoryRights(id):
    #data = 'data'
    con = sl.connect(data + '/datastories.db')
    cur = con.cursor()
    sql = "select v.email, v.name, v.eppn, r.rights from rights  r inner join visitors  v on r.eppn = v.eppn where r.story_uuid = '" + id + "'"
    print(sql)
    cur.execute(sql)
    names = list(map(lambda x: x[0], cur.description)) # ergens opgezocht
    result = cur.fetchall()
    con.commit()
    cur.close()
    con.close()
    struct = []
    for x in result:
    # print('x', x[1])
    # id = x[1]
    # structure.append({'uuid': id})
        row = {}
    # namen in het resultaat plakken y is een rangnummer in de namenlijst
        for y in range(0, len(names)):
            key = names[y]
            value = x[y]
            row[key] = value
        # s.append({key: value})
        struct.append(row)
    return struct


def set_status(id, status):
    #data = 'data'
    con = sl.connect(data + '/datastories.db')
    cur = con.cursor()
    sql = "UPDATE stories SET status= '" + status +"' WHERE uuid = '" + id + "'"
    cur.execute(sql)
    con.commit()
    cur.close()
    con.close()
    return {"status": "OK"}

def getDataStoriesDB(auth_status):
    #data = 'data'
    con = sl.connect(data + '/datastories.db')
    cur = con.cursor()
    if auth_status["logged_in"] == "yes":
        sql = "SELECT uuid, title, status, strftime('%d-%m-%Y', created) as created, strftime('%d-%m-%Y (%H:%M)',modified) as modified, owner, eppn, groep FROM stories ORDER BY modified DESC"
    else:
        sql = "SELECT uuid, title, status, strftime('%d-%m-%Y', created) as created, strftime('%d-%m-%Y (%H:%M)',modified) as modified, owner, eppn, groep FROM stories WHERE status = 'P' ORDER BY title"
    cur.execute(sql)
    names = list(map(lambda x: x[0], cur.description)) # ergens opgezocht
    result = cur.fetchall()
    cur.close()
    con.close()

    struct = []
    for x in result:
        # print('x', x[1])
        # id = x[1]
        # structure.append({'uuid': id})
        row = {}
        # namen in het resultaat plakken y is een rangnummer in de namenlijst
        for y in range(0, len(names)):
            key = names[y]
            value = x[y]
            row[key] = value
            # s.append({key: value})
        if row["eppn"] == auth_status["eppn"]:
            row["rights"] = "RWDCS"
        else:
            rights = get_rights(row["uuid"], auth_status["eppn"])
            if rights:
                row["rights"] = rights[0]["rights"]
            else:
                row["rights"] = "-----"
        if row["status"] == 'P' or not row["rights"] == "-----":
            struct.append(row)

    return struct

def add_rights_to_storylist(list, eppn):
    retList = []
    for item in list:
        rights = get_rights(item["uuid"], eppn)
        if rights:
            item["rights"] = rights[0]["rights"]
        retList.append(item)
    return retList

def get_item_rights(uuid, auth_status):
    retStr = "-----"
    if (auth_status["logged_in"] == 'yes'):
        if is_owner(auth_status["eppn"], uuid):
            retStr = 'RWDCS'
        else:
            rights = get_rights(uuid, auth_status["eppn"])
            if rights:
                retStr = rights[0]["rights"]
    return retStr

def get_rights(uuid, eppn):
    sql = "SELECT rights FROM rights WHERE story_uuid = ? AND eppn = ?"
    values = (uuid, eppn)
    result = fetch_data(sql, values)
    return result

def is_owner(eppn, uuid):
    sql = "SELECT id FROM stories WHERE eppn = ? AND uuid = ?"
    values = (eppn, uuid)
    result = fetch_data(sql, values)
    if result:
        return True
    else:
        return False

def getListUUIDs():
    #data = 'data'
    con = sl.connect(data + '/datastories.db')
    cur = con.cursor()   
    sql = "SELECT uuid FROM stories"
    cur.execute(sql)
    result = cur.fetchall() # list of tuples
    res = [ele[0] for ele in result] # list comprehension
    cur.close()
    con.close()
    return list(res)



def tooManyStories(max):
    #data = 'data/'
 
    count = len(os.listdir(data))
    print('aantal dirs', count)
    if(count > max):
        return True
    else:
        return False

def getNewId(auth_status):
    # maakt gebruik van een sql lite database voor gegarandeerde oplopende unieke ids
    unique_id = str(uuid.uuid4()) # kan misschien ook als database functie
    status = 'draft' # dubbelop?
    title = '[UNTITLED]'
    now = datetime.now(tz=ZoneInfo("Europe/Amsterdam"))
    created = now.strftime("%Y-%m-%d %H:%M:%S")    # creation timestamp
    print('datestring',created)
    # YYYY-MM-DD hh:mm:ss' 

    # datum = 
    # print('ideetje', ideetje)
    con = sl.connect(data + '/datastories.db')
    cur = con.cursor()   

    sql = "INSERT INTO stories (status, uuid, owner, eppn, title, groep, created, modified) values(?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))"
    value = ('D', unique_id, auth_status["user"], auth_status["eppn"], title, 'HuC')

    cur.execute(sql, value)
    con.commit()
    # id = con.lastrowid #werkt niet bij deze versie van sqllite
    res = cur.execute("SELECT last_insert_rowid()")
    con.commit()
    id = res.fetchone()
    unique_id = id[0]
    sql = 'SELECT id, uuid FROM stories WHERE id = ? '
    value = [unique_id]        
    cur.execute(sql, value)
    con.commit()
    result = res.fetchall()

    cur.close()
    con.close()

    # print('result', result)
    return result[0][1]

def createDataStoryFolder(id, template):
    # misschien ook een eens hiernaar kijken https://stackoverflow.com/questions/273192/how-do-i-create-a-directory-and-any-missing-parent-directories
    # os.path kan wel eens misgaan begrijp ik
    #data = 'data/'
    createDataFolder()
    directory = data + str(id)
    if not os.path.exists(directory):
        os.makedirs(directory)
        os.makedirs(directory + '/resources/images/')
        os.makedirs(directory + '/resources/audio/')
        os.makedirs(directory + '/resources/video/')
        saveDataStory(id, template)

    return True

def deleteDataStoryFolder(uuid):
    #data = 'data/'
    directory = data + str(uuid)
    if os.path.exists(directory):
        # os.removedir
        shutil.rmtree(directory)
        return True
    else:
        return False    
    

def removeFromDB(uuid):
    con = sl.connect(data + 'datastories.db')
    cur = con.cursor()
    sql = 'DELETE FROM stories WHERE uuid = ? '
    cur.execute(sql, (uuid,))
    con.commit()

    cur.close()
    con.close()

    return True

def updateModifiedDate(unique_id, title):
    now = datetime.now(tz=ZoneInfo("Europe/Amsterdam"))
    modified = now.strftime("%Y-%m-%d %H:%M:%S")    # creation timestamp
    con = sl.connect(data + '/datastories.db')
    cur = con.cursor()   
    sql = 'UPDATE stories SET title = ?, modified = ? WHERE uuid = ?  '
    print(sql)
    value = (title, modified, unique_id)
    print(value)
    cur.execute(sql, value)
    con.commit()
    # best practice https://stackoverflow.com/questions/5504340/python-mysqldb-connection-close-vs-cursor-close
    cur.close()
    con.close()
  
    

def fs_tree_to_dict(path_):
    file_token = ''
    for root, dirs, files in os.walk(path_):
        tree = {d: fs_tree_to_dict(os.path.join(root, d)) for d in dirs}
        tree.update({f: file_token for f in files})
        return tree  # note we discontinue iteration trough os.walk

# https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python
# Mikaelblomkvistsson's antwoord bijna onderaan, dit is de meest flexibele m.i. maar ik snap hem niet echt, nu geen tijd



def getDataStory(uuid):
    directory = data + "/" + str(uuid) # misschien niet meer nodig
    filename = directory + '/datastory.json'
    datastory = {}
    if os.path.exists(filename):
        with open(filename) as json_file:
            datastory = json.load(json_file)
    return datastory



def saveDataStory(datastory_id, datastory):
    path = data + str(datastory_id) + "/datastory.json"

    with open(path, 'w') as f:
        json.dump(datastory, f)
