from boto.dynamodb2.exceptions import ItemNotFound

def delete_by_id(table, request):
	try:
		id = request['id']
		item = table.get_item(id=int(id), consistent=True)
		if item.delete():
				#response.status = 200
		 		return {"data": {
		 							"type": "person", "id": id,
		 					}, "msg_id" : request['msg_id'], "status" : 200}
	 	else:
	 			#response.status = 500
		 		return {"errors": [{
		 							"id_exists": {
		 								"title": "delete operation cannot complete",
		 								"id": id,}
		 							}], "msg_id" : request['msg_id'], "status" : 404
							}

	except ItemNotFound as inf:
			#response.status = 404
			return {"errors": [{
								"not_found": { "id": id, }
								}], "msg_id" : request['msg_id'], "status" : 404
							}

def delete_by_name(table, request):
		try:
				name = request['name']
				items = table.scan(name__eq=name)
				for item in items:
						user = item
				 		id = item['id']
				
				try:
					 user.delete()
					 #response.status = 200
					 return {"data": { 
					 			"type": "person",
								"id": int (id),
					 			}, "msg_id" : request['msg_id'], "status" : 200
					 		}
				except Exception as e:
					 #response.status = 404
					 return {"errors": [{
					 "not_found": {
					 "name": name,
					 }
					 }], "msg_id" : request['msg_id'], "status" : 404
					 } 

		except ItemNotFound as inf:
					#response.status = 404
					return {"errors": [{
					"not_found": {
					"name": name,
					}
					}], "msg_id" : request['msg_id'], "status" : 404
					}


def delete_activity(table, request):
	try:
		id = request['id']
		item = table.get_item(id=int(id), consistent=True)
		activity = request['activity']

	except ItemNotFound as inf:
		#response.status = 404
		return {"errors": [{
				"not_found": {
				"id": id,
				}}],
				 "msg_id" : request['msg_id'], 
				 "status" : 404}

	if item['activities']:
			if activity in item['activities']:
					item['activities'].remove(activity)
					item.save()
					isActivityExist = True
			else:
					isActivityExist = False
	else:
			isActivityExist = False

	if isActivityExist:
		#response.status = 200 # "Updated"
		
		return {"data": {
						"type": "person",
						"id": id,
						"deleted": [activity] 
						}, "msg_id" : request['msg_id'], "status" : 200}
	else:
		#response.status = 404 # "Updated"
		return {"errors": [{
							"not_found": { "id": id }
						}], "msg_id" : request['msg_id'], "status" : 404
					}
