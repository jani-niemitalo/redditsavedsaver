#!/usr/bin/env python3
import mimetypes
import time
import requests
import requests.auth
import json
import os

token = ""


def main():
    client_auth = requests.auth.HTTPBasicAuth('***REMOVED***', '***REMOVED***')
    post_data = {"grant_type": "password", "username": "***REMOVED***", "password": "***REMOVED***"}
    headers = {"User-Agent": "Test custom user agent by ***REMOVED***"}
    response = requests.post("https://www.reddit.com/api/v1/access_token",
                             auth=client_auth,
                             data=post_data,
                             headers=headers)
    global token
    token = response.json()["access_token"]


def getExample():
    global token
    headers = {"Authorization": "bearer " + token,
               "User-Agent": "Test custom user agent by ***REMOVED***"}
    response = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers)
    print(response)


def getSaved():
    headers = {"Authorization": "bearer " + token,
               "User-Agent": "Test custom user agent by ***REMOVED***"}
    response = requests.get("https://oauth.reddit.com/user/***REMOVED***/saved" + "?count=25&sort=new",
                            headers=headers)
    response.json()
    filtered = filterSaved(response.json())
    return filtered

def getAllSaved():
    global token
    results = []
    after = ""
    while after is not None:
        time.sleep(1)
        headers = {"Authorization": "bearer " + token,
                   "User-Agent": "Test custom user agent by ***REMOVED***"}
        response = requests.get("https://oauth.reddit.com/user/***REMOVED***/saved" + "?count=25&after=" + after, headers=headers)
        response.json()
        after = response.json()["data"]["after"]
        filtered = filterSaved(response.json())
        print(after)
        for fitem in filtered:
            results.append(fitem)
    return results

def filterSaved(saved_items):
    result = []
    for item in saved_items["data"]["children"]:
        image_obj = {
            "name": item["data"]["id"],
            "url": item["data"]["url"],
            "permalink": item["data"]["permalink"],
        }
        result.append(image_obj)
    return result

class SaveFileManager:
    def __init__(self):
        self.save_object = []
        self.getSaveObj()

    def getSaveObj(self):
        try:
            fp = open("data/save.json")
            result = fp.read()
            save_data = json.loads(result)
            self.save_object = save_data
            fp.close()
        except:
            print("No file, or empty file")

    def setSaveObj(self):
        fp = open("data/save.json", "w+")
        json_string = json.dumps(self.save_object)
        fp.write(json_string)
        fp.close()

    def pushArrToSaved(self, filtered_items):
        for item in filtered_items:
            if item not in self.save_object:
                self.save_object.append(item)

    def pushObjToSaved(self, obj):
        if obj not in self.save_object:
            self.save_object.append(obj)

    def getSave(self):
        return self.save_object


def createFileDirs():
    # define the name of the directory to be created
    path = "./savedImages"
    path2 = "./data"

    # define the access rights
    access_rights = 0o755

    try:
        os.mkdir(path, access_rights)
    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s" % path)

    try:
        os.mkdir(path2, access_rights)
    except OSError:
        print("Creation of the directory %s failed" % path2)
    else:
        print("Successfully created the directory %s" % path2)

    try:
        test_file = "./savedImages/verify"
        f = open(test_file, "w+")
        f.close()
        os.remove(test_file)
        return True
    except:
        return False


def downloadItem(item, existings=[]):
    if item not in existings:
        print("Downloading " + item["name"])
        try:
            r = requests.get(item["url"], allow_redirects=True)
            extension = mimetypes.guess_extension(r.headers["content-type"])
            if not extension:
                print("NO EXTENSION DETECTED!!")
                print(extension)
                print(r)
                return False
            file = open("./savedImages/" + item["name"] + extension, 'wb')
            file.write(r.content)
            file.close()
            print("./savedImages/" + item["name"] + extension + " Created...")
            return item
        except Exception as e:
            print(e)
            print("Error downloading " + item["name"])
            return False

def firstRun(SFM):
    try:
        open("data/verify").close()
    except:
        open("data/verify", "x")
        filtered = getAllSaved()
        downloaded_items = SFM.getSave()
        for fitem in filtered:
            result = downloadItem(fitem, downloaded_items)
            if result:
                SFM.pushObjToSaved(result)

if __name__ == "__main__":
    SFM = SaveFileManager()
    # execute only if run as a script
    if not createFileDirs():
        exit(1)
    main()
    firstRun(SFM)
    # getExample()
    filtered_items = getSaved()
    downloaded_items = SFM.getSave()
    count = 0
    for fitem in filtered_items:
        result = downloadItem(fitem, downloaded_items)
        if result:
            SFM.pushObjToSaved(result)
            count += 1
    SFM.pushArrToSaved(filtered_items)
    SFM.setSaveObj()
    print("Downloaded " + str(count) + " items...")

