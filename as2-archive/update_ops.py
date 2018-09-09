''' Add_activities function for CMPT 474 Assignment 2 '''

from boto.dynamodb2.exceptions import ItemNotFound

def add_activity(table, id, activity, response):
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

    isActivityExist = False;

    if not item['activities']: 				#if activities field hasn't been created create a new one
        item['activities'] = set()			#must be a set()
	if not activity in item['activities']:
            item['activities'].add(activity)		#add function adds to the list
            item.partial_save()				#use partial_save or force save 
        else:
            isActivityExist = True;
    else:
        if not activity in item['activities']:
            item['activities'].add(activity)		
            item.partial_save()				#use partial_save or force save 
        else:
            isActivityExist = True;

    if not isActivityExist:
        response.status = 200 # "Updated"

        return {"data": {
            "type": "person",
            "id": id,
            "added": [activity]
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
