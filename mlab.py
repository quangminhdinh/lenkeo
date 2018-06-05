import mongoengine

#mongodb://<dbuser>:<dbpassword>@ds117136.mlab.com:17136/lincognito

host = "ds247330.mlab.com"
port = 47330
db_name = "lenkeo"
user_name = "admindeptrai"
password = "admin123"


def connect():
    mongoengine.connect(db_name, host=host, port=port, username=user_name, password=password)

def list2json(l):
    import json
    return [json.loads(item.to_json()) for item in l]


def item2json(item):
    import json
    return json.loads(item.to_json())
