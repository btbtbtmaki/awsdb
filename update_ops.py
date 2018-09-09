from boto.dynamodb2.exceptions import ItemNotFound

def add_activity(table, request):
	
	try:
		activity = request["activity"]
		id = request['id']
		item = table.get_item(id=int(id), consistent=True)
		

	except ItemNotFound as inf:
		return {"errors": [{
							"not_found": { "id": id}
						}], "msg_id" : request['msg_id'], "status" : 404
					}

	isActivityExist = False

	if not item['activities']: 				#if activities field hasn't been created create a new one
			item['activities'] = set()			#must be a set()
		
			if not activity in item['activities']:
					item['activities'].add(activity)		#add function adds to the list
					item.partial_save()				#use partial_save or force save 
			else:
					isActivityExist = True
	else:
			if not activity in item['activities']:
					item['activities'].add(activity)
					item.partial_save()				#use partial_save or force save 
			else:
					isActivityExist = True
	
	if not isActivityExist:
			return {"data": { 
						"type": "person",
						"id": id,
						"added": [activity]
						}, "msg_id" : request['msg_id'], "status" : 200
						}
	else:
			return {"errors": [{
								"not_found": { "id": id }
							}], "msg_id" : request['msg_id'], "status" : 404
						}
