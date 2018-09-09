''' Retrieve operations for CMPT 474 Assignment 2 '''

from boto.dynamodb2.exceptions import ItemNotFound

def retrieve_by_id(table, id, response):
    try:
        item = table.get_item(id=id)
        activities=[]
        if item['activities'] is not None:
        	for activity in item['activities']:
        		activities.append(activity)

        response.status = 200
        return {"data": {
                str("type"): str("person"),
                str("name"): item['name'],
                str("id"): int(id),
                str("activities"): activities
                }
        	} 
    except ItemNotFound as inf:
        response.status = 404
        return {"errors": [{
                "not_found": {
                    "id": id,
                }
            }]
        }

def retrieve_by_name(table, name, response):
    try:										#see if the user actually exist, if not threw exception
        items = table.scan(name__eq =name) 		#scan the table with condition name==name
        for x in items: idc = x['id']			#since we assume there will be no duplicate name, only one item returns
		
	item = table.get_item(id = idc)				#retrieve the item with its primary key
	activities=[]								#setup return activities array
	if item['activities'] is not None:			#check if there is activity for the item, if yes, add them to activities array
		for activity in item['activities']:
			activities.append(activity)			#note here the activities must be a list of strings field instead of just string field
	
	response.status = 200						#im not sure if it matter, but it did not pass the test, so casting to string
	return {"data": {
			str("type"): str("person"),
			str("name"): str(name),
			str("id"): int(idc),
			str("activities"): activities
			}
			} 
	
    except ItemNotFound as inf:
        response.status = 404
        return {"errors": [{
                "not_found": {
                    "name": name,
                }
            }]
        }
#following function worked by kca101
def retrieve_list_users(table,response):
    try:
        
        users=[]
        results = table.scan()
    
        for user in results:
            string = {"type":"users","id": int(user["id"])} 
            users.append(string)

        response.status = 200
        return {"data" :users

            } 
    except ItemNotFound as inf:
        response.status = 404
        return {"errors"
        }
      
          
