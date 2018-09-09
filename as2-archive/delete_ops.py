''' Delete operations for Assignment 2 of CMPT 474 '''

# Installed packages

from boto.dynamodb2.exceptions import ItemNotFound

def delete_by_id(table, id, response):
    try:
        item = table.get_item(id=id)

        if item.delete():
            response.status = 200
            return {"data": {
                        "type": "person",
                        "id": id,
                    }
                }
        else:
            response.status = 500
            return {"errors": [{
                        "id_exists": {
                            "title": "delete operation cannot complete",
                            "id": id,
                        }
                    }]
                }

    except ItemNotFound as inf:
        response.status = 404
        return {"errors": [{
                    "not_found": {
                        "id": id,
                    }
                }]
            }


def delete_by_name(table, name, response):
    try:
        items = table.scan(name__eq=name)  

        for item in items:
            user = item
            id = item['id']

        try:
            user.delete()
            response.status = 200
            return {"data": {
                        "type": "person",
                        "id": int (id),
                    }
                }
        except Exception as e:
            response.status = 404
            return {"errors": [{
                    "not_found": {
                    "name": name,
                    }
                }]
            } 
       
    except ItemNotFound as inf:
        response.status = 404
        return {"errors": [{
                "not_found": {
                    "name": name,
                }
            }]
        }


def delete_activity(table, id, activity, response):
    try:
        item = table.get_item(id=id)

    except ItemNotFound as inf:
        response.status = 404
        return {"errors": [{
                "not_found": {
                    "id": id,
                }
            }]
        }


    if item['activities']:
        if activity in item['activities']:
            item['activities'].remove(activity)
            item.save()
            isActivityExist = True;
        else:
            isActivityExist = False;
    else:
        isActivityExist = False;

    if isActivityExist:
        response.status = 200 # "Updated"

        return {"data": {
            "type": "person",
            "id": id,
            "deleted": [activity]
            }
        }
    else:
        response.status = 404 # "Updated"

        return {"errors": [{
            "not_found": {
            "id": id
 		}           
            }]
        }
