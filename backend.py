#!/usr/bin/env python

'''

'''

# Library packages
import argparse
import json
import sys
import time

# Installed packages
import boto.dynamodb2
from boto.dynamodb2.items import Item
import boto.dynamodb2.table
from boto.dynamodb2.exceptions import ItemNotFound
import boto.sqs
import boto.sqs.message
from boto.sqs.message import Message

# debugs
from logger import log_back, log_fail, log_warning, log_status
# backend operations
from create_ops import create_user
from retrieve_ops import retrieve_by_id, retrieve_by_name, retrieve_list_users
from delete_ops import delete_by_id, delete_by_name, delete_activity
from update_ops import add_activity

import constants


TABLE_NAME_BASE = "activities"
Q_IN_NAME_BASE = "a3_back_in"

MAX_TIME_S = 3600 # One hour
MAX_WAIT_S = 20 # SQS sets max. of 20 s
DEFAULT_VIS_TIMEOUT_S = 60
#Added constants---------------------------------------------------------------------------


#need a method to handle them accordingly: _a or _b
# defualt queue
QUEUE_IN = "a3_in_a"
TABLE_NAME = "activities" #Default Name


#--------------------------------------------------------------------------------------
def handle_args():
	argp = argparse.ArgumentParser(
		description="Backend for simple database")
	argp.add_argument('suffix', help="Suffix for queue base ({0}) and table base ({1})".format(Q_IN_NAME_BASE, TABLE_NAME_BASE))
	return argp.parse_args()


#Operations--------------------------------------------------------------------------------------------
#function for creating or connecting sqs queue
def create_q(name):
	try:
		conn = boto.sqs.connect_to_region(constants.AWS_REGION)
		if conn == None:
			sys.stderr.write("Could not connect to AWS region '{0}'\n".format(constants.AWS_REGION))
			sys.exit(1)

	except Exception as e:
				sys.stderr.write("Exception connecting to SQS\n")
				sys.stderr.write(str(e))
				sys.exit(1)

	# create_queue is idempotent---if queue exists, it simply connects to it
	return conn.create_queue(name)

def write_out_msg(rqResult):
	global nextTopNum
	msg_out.set_body(json.dumps(rqResult))
	msgIDList[key] = msg_out
	qout.write(msg_out)
	nextTopNum += 1
	log_back("RESPONSE TO FRONTEND: " + msg_out.get_body())
'''

'''

#connecting to table
def main():
	global table
	try:
		conn_table = boto.dynamodb2.connect_to_region(constants.AWS_REGION)
		if conn_table == None:
			sys.stderr.write("Could not connect to AWS region '{0}'\n".format(contants.AWS_REGION))
			sys.exit(1)

		table = boto.dynamodb2.table.Table(TABLE_NAME, connection=conn_table)

	except Exception as e:
			sys.stderr.write("Exception connecting to DynamoDB table {0}\n".format(TABLE_NAME))
			sys.stderr.write(str(e))
			sys.exit(1)


if __name__ == "__main__":
		args = handle_args()
		QUEUE_IN = Q_IN_NAME_BASE + args.suffix               #reset the name of of the qin to add suffix
		#print QUEUE_IN
		TABLE_NAME = TABLE_NAME_BASE + args.suffix              #reset the name of the table to add suffix
		#creating qin, qout and table-----------------------------------------------------------------
		qin = create_q(QUEUE_IN)
		qout = create_q(constants.Q_OUT_NAME)
		global nextTopNum  	#this is next expected op num, starts at 1
		nextTopNum = 1
		requestList = [] #we use a dictonary to store out of order msg
		global msgIDList  #we choose to use a dictionary to track operations, the msg_id is the key, output response is the stored value
		msgIDList = {}
		request = {}	#creating globa(while loop) request variable
		main()          #connect to table
		log_status("#########    BACKEND RUNNING    ##########")
		while True:
				#always check to see if the next expected op is stored first
				#If it's found, skip read in from inqueue
				skip_read_in = 0
				index = 0
				for req in requestList:
					if req['opnum'] <= nextTopNum:
						request = req
						skip_read_in = 1
						requestList.pop(index)
						#del requestList[operation]
						break
					index += 1 

				#If it's not found, reading in from qin

				if skip_read_in == 0:
					msg_in = qin.read(DEFAULT_VIS_TIMEOUT_S)
					if msg_in == None:
						continue
					log_back("REQUEST FROM FRONTEND: " + msg_in.get_body())
					request = json.loads(msg_in.get_body())
					qin.delete_message(msg_in)


				#if function to find out of order ops ##############################################################
				#if the request is out of order, add it to the storage, start from beginning.

				if request['opnum'] > nextTopNum:
					requestList.append(request)
					continue



				#if loop to determine operations#####################################################################
				# The ops codes are as followed
				# create_route:     		post_users
				# add_activity_route: 		put_activity_by_activity_name
				# get_id_route:     		get_user_by_id
				# get_user_route:     		get_users
				# get_name_route:     		get_user_by_name
				# delete_id_route:    		delete_user_by_id
				# delete_name_route:  		delete_user_by_name
				# delete_activity_route:	delete_activity_by_activity_id

				duplicated_flag = 0 					#The duplicated_flag is used to skip the if loops for duplicated operation
				for msgID in msgIDList:					#This part of code tests for duplicates, if the msg_id is in the dictonary, skip if loops and send back original response
					if msgID == request['msg_id']:
							log_warning("REPLICATED msg_in: " + request['msg_id'])
							qout.write(msgIDList[msgID])
							duplicated_flag = 1
							break

				if duplicated_flag == 1: continue
				if request['method'] == None:
						log_fail("INVALID METHOD ID " + request['msg_id'])
						continue


				#print opnum of the request
				log_back("###### EXPECTED OP# : " + str(nextTopNum))
				log_back("!!!!!! REQUEST OP# : " + str(request['opnum']))

				msg_out = Message()				#creating empty message object for msg_out
				key = request['msg_id']			#assigning msg_id to key
				#print "line 413", key
				method = request['method']
				if method == constants.METHOD_POST_USER:
						rqresult = create_user(table,request)
						#rqresult['backend'] = args.suffix
						write_out_msg(rqresult)
						log_back("#####	created user    #####\n")

				elif method == constants.METHOD_GET_USER_BY_ID:
						rqresult = retrieve_by_id(table, request)
						#rqresult['backend'] = args.suffix
						write_out_msg(rqresult)
						log_back("#####	got user by id 	 #####\n")

				elif method == constants.METHOD_GET_USERS:
						rqresult = retrieve_list_users(table, request)
						#rqresult['backend'] = args.suffix
						write_out_msg(rqresult)
						log_back("#####	Retrieved users    #####\n")

				elif method == constants.METHOD_DELETE_USER_BY_ID:
						rqresult = delete_by_id(table, request)
						#rqresult['backend'] = args.suffix
						write_out_msg(rqresult)
						log_back("#####	Deleted user by id    #####\n")

				elif method == constants.METHOD_GET_USER_BY_NAME:
						rqresult = retrieve_by_name(table, request)
						#rqresult['backend'] = args.suffix
						write_out_msg(rqresult)
						log_back("#####	Retrieved by name     #####\n")

				elif method == constants.METHOD_DELETE_USER_BY_NAME:
						rqresult = delete_by_name(table, request)
						#rqresult['backend'] = args.suffix
						write_out_msg(rqresult)
						log_back("#####	Deleted by name    #####\n")

				elif method == constants.METHOD_PUT_ACTIVITY_BY_ACTIVITY_NAME:
						rqresult = add_activity(table, request)
						#rqresult['backend'] = args.suffix
						write_out_msg(rqresult)
						log_back("#####	added activity by name    #####\n")

                                elif method == constants.METHOD_DELETE_ACTIVITY_BY_ACTIVITY_NAME:
						rqresult = delete_activity(table, request)
						#rqresult['backend'] = args.suffix
						write_out_msg(rqresult)

						log_back("#####	Deleted activity by name    #####\n")

				else:
						log_fail("INVALID OPERATION: " + key)
						continue  #continue to get next message, current message treat as invalid for now
				log_back("!!!!!! NEXT EXPECTED OP# : " + str(nextTopNum))
				log_back("#########	BACKEND WORKING		##########")

		#-------------------------------------------------------------------------

