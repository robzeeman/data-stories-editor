import json
from typing import Union, Annotated
import uvicorn
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Depends, Body
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from auth import router as auth_router
from starlette.requests import Request
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from ds_template import template
from os.path import exists
from functions import (
    getNewId, createDataStoryFolder, removeFromDB,
    deleteDataStoryFolder,getDataStory, getDataStorySettings, fs_tree_to_dict,
    tooManyStories, createDataFolder, set_status, createDataStoriesDB, getDataStoriesDB,
    getListUUIDs, updateModifiedDate, saveDataStory, uri_validator, get_setting_users, add_user_rights, revoke_user_rights,
    save_user_rights_str, get_item_rights, get_message
)
from request_types import (UrlType, SettingStatus, UserRights, DataStory)
from dependencies import authenticated_user
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from config import DATA_LOCATION, ds_app_url
from pathlib import Path


app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key='dkhkajhdlkhdkkk')
app.add_middleware(CORSMiddleware, allow_origins=[ds_app_url], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.include_router(auth_router)




# @app.get("/")
# def hello_world():
#     retStruc = {"app": "CLARIAH Data Stories Service", "version": "1.0"}
#     # jsonHeaders(response)
#     return RedirectResponse("http://localhost/app")

@app.post("/check_url")
def check_url(data: UrlType):
    url = data["url"]
    result = uri_validator(url)
    return {"status": result}

@app.get("/get_settings")
async def settings(ds: str):
    return getDataStorySettings(ds)

@app.post('/set_settings')
def set_settings(data: SettingStatus):
    result = set_status(data["id"], data["status"])
    return result

@app.get("/get_setting_users")
def setting_users(ds: str):
    status = get_auth_status()
    result = get_setting_users(ds, status["eppn"])
    return result

@app.post("/save_user_rights")
def save_user_rights(data: UserRights):
    status = get_auth_status()
    if status["logged_in"] == "yes":
        save_user_rights_str(data["uuid"], data["eppn"], data["rights"])
    return {"status": "OK"}


@app.get("/add_user_rights")
def add_rights(ds: str, eppn: str):
    status = get_auth_status()
    if status["logged_in"] == "yes":
        add_user_rights(ds, eppn)
    return {"status": "OK"}

@app.get("/revoke_user_rights")
def revoke_rights(ds: str, eppn: str):
    status = get_auth_status()
    if status["logged_in"] == "yes":
        revoke_user_rights(ds, eppn)
    return {"status": "OK"}

@app.get("/create_new")
def create_new():
    status = get_auth_status()
    max = 100 # maximaal 100 datastories
    if tooManyStories(max) or status["logged_in"] == "no":
        response = {"status": 'ff aan de rem getrokken'}
        return response

    id = getNewId(status)
    status = createDataStoryFolder(id, template)
    if status == True:
        # stringie = 'I created something new! De unieke id is: ' + str(id)
        response = {"datastory_id": id}
        return response

@app.get("/delete")
def delete(ds: str):
    if deleteDataStoryFolder(ds):
        status = 'OK'
    else:
        status = 'DATASTORY NOT FOUND'

    removeFromDB(ds) # nog even goed naar kijken of dit nu klopt
    response = {"status": status}
    return response

# datastory is de inhoud van de json file, ik hoef geen structuur te parsen
@app.get("/get_item")
async def get_item(ds: str, userdata: Annotated[dict | None, Depends(authenticated_user)]):
    datastory = {}
    uuid = ds
    status = get_auth_status(userdata)
    status["rights"] = get_item_rights(uuid, status)
    #print('uuid', uuid)
    if not uuid:
        status = 'INVALID REQUEST, NO UUID'

    else:
        datastory = getDataStory(uuid) # kan empty zijn

    response = {"status": status, "datastory": datastory}
    return response


# hier moet de sqllite database bevraagd worden, om de lijstpagina te genereren
@app.get("/get_data_stories")
async def getDataStories(userdata: Annotated[dict | None, Depends(authenticated_user)]):
    status = 'OK'
    auth_status = get_auth_status(userdata)
    structure = getDataStoriesDB(auth_status)
    message = get_message()
    response = {"status": status, "auth": auth_status, "structure": structure, "message": message}
    return response


@app.post("/update_datastory")
async def updateDataStory(request: Request):
    data = await request.json()
    datastory_id = data["datastory_id"]
    datastory_title = data["datastory_title"]
    datastory = data["datastory_file"]

    # save the content to file
    #path = "data/" + str(datastory_id) + "/datastory.json"

    #with open(path, 'w') as f:
    #    json.dump(datastory, f)
    saveDataStory(datastory_id, datastory)
    updateModifiedDate(datastory_id, datastory_title)

    return {"status": "OK"};

# ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# def allowed_file(filename):
# 	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.get('/login', methods = ["GET"])
# def login():
#     session['logged_in'] = "yes"
#     session['user'] = "Rob Zeeman"
#     return(jsonify({"status": "ok", "logged_in": session.get('logged_in')}))


@app.post('/upload')
async def upload(file: UploadFile, uuid: str = Form(...)):
    if not file:
        print('No file in request')
        return {"status": "No file in request"}

    if not uuid:
        print('No uuid')
        return {"status": "No uuid"}

    listUUIDS = getListUUIDs()
    # print(listUUIDS)
    if not uuid in listUUIDS:
        # print('zit er niet in')
        return {"status": "uuid not available"}

    filename =  file.filename

    #print("request.files['file'].filename: ", request.files['file'].filename)
    #print("request.files['file'].content_type: ", request.files['file'].content_type)

    # filename = uploaded_file.filename
    content_type = file.content_type

    resources = DATA_LOCATION + "/" + uuid + '/resources'

    if content_type.startswith('image'):
        store = resources + '/images/'
    elif content_type.startswith('audio'):
        store = resources + '/audio/'
    elif content_type.startswith('video'):
        store = resources + '/video/'
    else:
        return {"status": "Go Home!"}
        # exit()

    # https://tedboy.github.io/flask/generated/generated/werkzeug.FileStorage.html

    filepath = store + filename
    data = await file.read() # je moet de bytes readen uit een DataStorage Object
    with open(filepath, 'ab') as f:
        f.write(data)

    if exists(filepath):
        status = "OK"
    else:
        status = "NOT OK"

    return status

@app.get("/resources/{uuid}/{resourcetype}/{filename}")
async def resources(uuid: str, resourcetype: str, filename: str):
    # we can severe the api from the real path, safer I think
    # TODO checks and balances maybe

    filepath: str = DATA_LOCATION + '/' +uuid + '/resources/' + resourcetype + '/' + filename

    # TODO mime-types? Or does send_file this..
    try:
        return FileResponse(filepath)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found!")

    # # read from file serve right mimetype
    # print(filepath)
    # status = 'OK'
    # return json.dumps(status)

# @app.get("/{path:path}")
# async def frontend_handler(path: str):
#     fp = Path("static") / path
#     if not fp.exists() or not fp.is_file():
#         fp = Path("static") / "index.html"
#     return FileResponse(fp)

def get_auth_status(user):
    #return {"logged_in": "yes", "user": "Rob Zeeman", "eppn": "3cc036843bde09c86580da2d3d753a527d1e8bfa"}
    if user:
        return {"logged_in": "yes", "user": user.name, "eppn": user.user_id}
    return {"logged_in": "no", "user": "", "eppn": ""}


app.mount("/", StaticFiles(directory="service/frontend", html=True), name="spa")

# if __name__ == "__main__":
#     uvicorn.run('main:app', host='0.0.0.0', port=80, timeout_keep_alive=60, reload=True,
#                 log_level='INFO'.lower())