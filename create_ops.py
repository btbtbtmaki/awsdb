from boto.dynamodb2.items import Item
from boto.dynamodb2.exceptions import ItemNotFound

def create_user(table, request):
	try:
		id = request['id']
		name = request['name']
		item = table.get_item(id=int(id), consistent=True)
		if item["name"] != name:
			return  {"errors": [{
			"id_exists": {
							"status": "400",      # "Bad Request"
							"title": "id already exists",
							"detail": {"name": item['name']}
							}
							}], "msg_id" : request['msg_id'], "status" : 400 
							}

	except ItemNotFound as inf:
			p = Item(table, data={'id': id, 'name': name, 'activities': set()})
			p.save()
		
	return {"data": 
						{"type": "person",
							"id": id,
							 "links": {
							 	"self": "{0}://{1}/users/{2}".format(request['scheme'], request['netloc'], id)
							 }
						}, "msg_id" : request['msg_id'], "status" : 201
					}   
