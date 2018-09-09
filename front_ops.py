'''
   Ops for the frontend of Assignment 3, Summer 2016 CMPT 474.
'''
import sys

# Standard library packages
import json

# Installed packages
import boto.sqs

# Imports of unqualified names
from bottle import post, get, put, delete, request, response

# Local modules
import SendMsg

# import logger
from logger import log_front
import constants

# global variables
global dups

# Define a ZooKeeper operation counter as global variable seq_num
def setup_op_counter():
    global seq_num
    zkcl = send_msg_ob.get_zkcl()
    if not zkcl.exists('/SeqNum'):
        zkcl.create('/SeqNum', "0")
    else:
        zkcl.set('/SeqNum', "0")

    seq_num = zkcl.Counter('/SeqNum')
    # When you need a fresh, unique counter value
    seq_num += 1

# Respond to health check
@get('/')
def health_check():
    response.status = 200
    return "Healthy"

# EXTEND:
# Define all the other REST operations here ...

# curl -i -X post -H 'Content-type: application/json' -d '{"id": 9370176, "name": "James Tiberius Kirk"}' http://localhost:8080/users
@post('/users')
def create_route():
    msg_body = request.json
    msg_body['method'] = constants.METHOD_POST_USER
    msg_body['scheme'] = request.urlparts.scheme
    msg_body['netloc'] = request.urlparts.netloc
    msg_body['opnum'] = seq_num.value
    return process_message(msg_body)

# curl -i -X put http://localhost:8080/users/9370176/activities/shouting
@put('/users/<id>/activities/<activity>')
def put_activity_route(id, activity):
    msg_body= dict(method=constants.METHOD_PUT_ACTIVITY_BY_ACTIVITY_NAME, id=id, activity=activity, opnum=seq_num.value)
    return process_message(msg_body)

# curl -i http://localhost:8080/users/9370176
@get('/users/<id>')
def get_id_route(id):
    msg_body = dict(method=constants.METHOD_GET_USER_BY_ID, id=id, opnum=seq_num.value)
    return process_message(msg_body)

# curl -i http://localhost:8080/users
@get('/users')
def get_user_route():
    msg_body = dict(method=constants.METHOD_GET_USERS, opnum=seq_num.value)
    return process_message(msg_body)

# curl -i http://localhost:8080/names/James%20Tiberius%20Kirk
@get('/names/<name>')
def get_name_route(name):
    msg_body = dict(method=constants.METHOD_GET_USER_BY_NAME, name=name, opnum=seq_num.value)
    return process_message(msg_body)

# curl -i -X delete http://localhost:8080/users/9370176
@delete('/users/<id>')
def delete_id_route(id):
    msg_body = dict(method=constants.METHOD_DELETE_USER_BY_ID, id=id, opnum=seq_num.value)
    return process_message(msg_body)

# curl -i -X delete http://localhost:8080/names/James%20Tiberius%20Kirk
@delete('/names/<name>')
def delete_name_route(name):
    msg_body = dict(method=constants.METHOD_DELETE_USER_BY_NAME, name=name, opnum=seq_num.value)
    return process_message(msg_body)

# curl -i -X delete http://localhost:8080/users/9370176/activities/shouting
@delete('/users/<id>/activities/<activity>')
def delete_activity_route(id, activity):
    msg_body = dict(method=constants.METHOD_DELETE_ACTIVITY_BY_ACTIVITY_NAME, id=id, activity=activity, opnum=seq_num.value)
    return process_message(msg_body)

def process_message(message_body):
    log_front("REQUEST TO BACKEND: " + str(message_body))

    # convert input to json object
    message = json.dumps(message_body)

    # initialize message and set their contents
    msg_a = boto.sqs.message.Message()
    msg_a.set_body(message)

    msg_b = boto.sqs.message.Message()
    msg_b.set_body(message)

    result = send_msg_ob.send_msg(msg_a, msg_b)
    response.status = result['status']

    log_front("RESPONSE TO END USER: " + str(message_body))

    return result

'''
   Boilerplate: Do not modify the following function. It
   is called by frontend.py to inject the names of the two
   routines you write in this module into the SendMsg
   object.  See the comments in SendMsg.py for why
   we need to use this awkward construction.

   This function creates the global object send_msg_ob.

   To send messages to the two backend instances, call

       send_msg_ob.send_msg(msg_a, msg_b)

       where

       msg_a is the boto.message.Message() you wish to send to a3_in_a.
       msg_b is the boto.message.Message() you wish to send to a3_in_b.

       These must be *distinct objects*. Their contents should be identical.
'''
def set_send_msg(send_msg_ob_p):
    global send_msg_ob
    send_msg_ob = send_msg_ob_p.setup(write_to_queues, set_dup_DS)

'''
   EXTEND:
   Set up the input queues and output queue here
   The output queue reference must be stored in the variable q_out
'''
try:
    conn = boto.sqs.connect_to_region(constants.AWS_REGION)
    if conn == None:
        sys.stderr.write("Could not connect to AWS region '{0}'\n".format(constants.AWS_REGION))
        sys.exit(1)

    # initialize dups variable
    dups = []
    # create_queue is idempotent---if queue exists, it simply connects to it
    q_in_a = conn.create_queue(constants.Q_IN_A_NAME)
    q_in_b = conn.create_queue(constants.Q_IN_B_NAME)
    q_out = conn.create_queue(constants.Q_OUT_NAME)

except Exception as e:
    sys.stderr.write("Exception connecting to SQS\n")
    sys.stderr.write(str(e))
    sys.exit(1)

def write_to_queues(msg_a, msg_b):
    # EXTEND:
    # Send msg_a to a3_in_a and msg-b to a3_in_b
    q_in_a.write(msg_a)
    q_in_b.write(msg_b)

'''
   EXTEND:
   Manage the data structures for detecting the first and second
   responses and any duplicate responses.
'''

# Define any necessary data structures globally here

def is_first_response(id):
    # EXTEND:
    # Return True if this message is the first response to a request
    for d in dups:
        if d.getIdA() == id or d.getIdB() == id:
            if d.getFirstResponse() == 0:
                return True;
    return False

def is_second_response(id):
    # EXTEND:
    # Return True if this message is the second response to a request
    for d in dups:
        if d.getIdA() == id or d.getIdB() == id:
            if d.getSecondResponse() == 0:
                return True;
    return False

def get_response_action(id):
    # EXTEND:
    # Return the action for this message
    for d in dups:
        if d.getIdA() == id or d.getIdB() == id:
            return d.getAction()

def get_partner_response(id):
    # EXTEND:
    # Return the id of the partner for this message, if any
    for d in dups:
        if d.getIdA() == id:
            return d.getIdB()
        elif d.getIdB() == id:
            return d.getIdA()

def mark_first_response(id):
    # EXTEND:
    # Update the data structures to note that the first response has been received
    for d in dups:
        if d.getIdA() == id or d.getIdB() == id:
            d.setFirstResponse(id)
            break;

def mark_second_response(id):
    # EXTEND:
    # Update the data structures to note that the second response has been received
    for d in dups:
        if d.getIdA() == id or d.getIdB() == id:
            d.setSecondResponse(id)
            break;

def clear_duplicate_response(id):
    # EXTEND:
    # Do anything necessary (if at all) when a duplicate response has been received
    tempList = dups
    for d in tempList:
        if d.getIdA() == id or d.getIdB() == id:
            dups.remove(d)

class DuplicatorRecord(object):
    def __init__(self, action, id_a, id_b):
        self.action = action
        self.id_a = id_a
        self.id_b = id_b
        self.first_response = 0
        self.second_response = 0

    def getAction(self):
        return self.action

    def getIdA(self):
        return self.id_a

    def getIdB(self):
        return self.id_b

    def setFirstResponse(self, id):
        self.first_response = id

    def getFirstResponse(self):
        return self.first_response

    def setSecondResponse(self, id):
        self.second_response = id

    def getSecondResponse(self):
        return self.second_response

def set_dup_DS(action, sent_a, sent_b):
    '''
       EXTEND:
       Set up the data structures to identify and detect duplicates
       action: The action to perform on receipt of the response.
               Opaque data type: Simply save it, do not interpret it.
       sent_a: The boto.sqs.message.Message() that was sent to a3_in_a.
       sent_b: The boto.sqs.message.Message() that was sent to a3_in_b.

               The .id field of each of these is the message ID assigned
               by SQS to each message.  These ids will be in the
               msg_id attribute of the JSON object returned by the
               response from the backend code that you write.
    '''
    dups.append(DuplicatorRecord(action, sent_a.id, sent_b.id))
    global seq_num
    seq_num += 1
