from boto.dynamodb2.exceptions import ItemNotFound

def retrieve_by_id(table, request):
	try:
		id = request['id']
		item = table.get_item(id=int(id), consistent=True)
		activities=[]

		if item['activities'] is not None:
				for activity in item['activities']:
						activities.append(activity)
						#response.status = 200

		return {"data": {
						str("type"): str("person"),
						str("name"): item['name'],
						str("id"): int(id),
						str("activities"): activities
					}, "msg_id" : request['msg_id'], "status" : 200}
	
	except ItemNotFound as inf:
			#response.status = 404
			return {"errors": [{ 
								"not_found": { "id": id, }
							}], "msg_id" : request['msg_id'], "status" : 404
						}

def retrieve_by_name(table, request):
	try:
			name = request['name']
			items = table.scan(name__eq =name)
			#if name is not exist
			isNameExist = False
			users=[]
			results = table.scan()
			for user in results:
					if user['name'] == name:
							isNameExist = True

			if isNameExist == False:
					return {"errors": [{
											"not_found" : { "name" : name, }
									}],
									"msg_id" : request['msg_id'], 
									"status" : 404
								}
			idc = 0
			for x in items:
					idc = x['id']
					item = table.get_item(id=int(idc), consistent=True)
			
			activities=[]
			if item['activities'] is not None:
					for activity in item['activities']:
							activities.append(activity)

			return {"data": {
						str("type"): str("person"),
						str("name"): str(name),
						str("id"): int(idc),
						str("activities"): activities
						}, "msg_id" : request['msg_id'], "status" : 200} 

	except ItemNotFound as inf:
			return {"errors": [{
							"not_found": {
								"name": name,
							}
							}], "msg_id" : request['msg_id'], "status" : 404
						}


def retrieve_list_users(table, request):
	try:
		users=[]
		results = table.scan()
		n = 0
		for user in results:
				string = {"type":"users","id": int(user["id"])} 
				users.append(string)
		
		return {"data" :users, "msg_id" : request['msg_id'], "status" : 200} 
	
	except ItemNotFound as inf:
			#response.status = 404
			return {"errors" : "errors" , "msg_id" : request['msg_id'], "status" : 404}
