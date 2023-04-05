#!/usr/bin/python3
import subprocess
import sys
import datetime as dt
import time
import threading
from termcolor import colored

base_path = subprocess.Popen("cd ~/Downloads && pwd", shell=True, text=True,
								stdout=subprocess.PIPE).stdout.read().rstrip('\n')+"/"
previous_execute_time = 0

def thread(devices, targ, *options):
	threads = []
	for device in devices:
		t = threading.Thread(target = targ , args = (device, *options,))
		threads.append(t)
	#excute thread
	for i in range(len(devices)):
		threads[i].start()
	#wait for end of t
	for i in range(len(devices)):
		threads[i].join()

# open cmd file and keep each command in cmds list
def list_cmd():
	cmds = []
	fr = open("./cmds", "r")
	for i in fr:
		cmds.append(i)
	return cmds

# subprocess
def process(cmd, dir):
	p = subprocess.Popen(cmd, shell=True, text=True, stdout=subprocess.PIPE,
							stderr=subprocess.STDOUT, cwd=dir, bufsize=-1)
	return p.stdout.read()

# get specific line
def select_line(string, line_index):
	return string.splitlines()[line_index]
   
# get data from log
def status(log,P,F,C,Run_time,A,I,T,remove):
	i = -1
	while True:
		tmp = select_line(log, i)
		if "PASSED            :" in tmp:	P = int(tmp[20:])
		elif "FAILED            :" in tmp:	F = int(tmp[20:]) 
		elif "ASSUMPTION_FAILURE:" in tmp: A = int(tmp[20:])
		elif "Total Tests" in tmp:	T = int(tmp[20:])
		elif "IGNORED           :" in tmp: I = int(tmp[20:])
		elif "IMPORTANT" in tmp:	C = False
		elif "Total Run time" in tmp:	Run_time = tmp[16:]
		elif "No modules found matching" in tmp:	remove = True
		elif "=============== Summary " in tmp: break
		i -= 1
	return P,F,C,Run_time,A,I,T,remove

# extract results time
def extract_time(target, log):
	i = 0
	while True:
		tmp = select_line(log, i)
		if target in tmp:
			Time = tmp[0:14]
			break
		i += 1
	Time = Time.replace(Time[2], '.').replace(Time[5],'_').replace(':','.')	
	return Time

# get results session
def get_session(log, pre_Time, Time, pre_session_fail, session, unknown):
	tTime = Time
	for x in log.splitlines():
		#inscase new result worst than previous, consider multiple machine running
		tmp = 0
		if pre_Time in x:
			tmp = int(x[0:3])

		if tTime in x:
			if "unknown" in x:
				unknown = True
				break
			pre_Time = tTime
			try:
				pre_session_fail = int(x[15:20])
			except:
				pre_session_fail = int(x[18:23])
			session = int(x[0:3])
			break
		elif tTime[0:12]+'09' in x:
			Time = tTime[0:12]+'09'
			if "unknown" in x:
				unknown = True
				break
			pre_Time = Time
			try:
				pre_session_fail = int(x[15:20])
			except:
				pre_session_fail = int(x[18:23])
			session = int(x[0:3])
			break
		elif tTime[0:13]+str(int(tTime[13])-1) in x:
			Time = tTime[0:13]+str(int(Time[13])-1)
			if "unknown" in x:
				unknown = True
				break
			pre_Time = Time
			try:
				pre_session_fail = int(x[15:20])
			except:
				pre_session_fail = int(x[18:23])
			session = int(x[0:3])
			break	
		elif tTime[0:12] + str(int(tTime[-2:])-1) in x:
			Time = tTime[0:12] + str(int(tTime[-2:])-1)
			if "unknown" in x:
				unknown = True
				break
			pre_Time = Time
			try:
				pre_session_fail = int(x[15:20])
			except:
				pre_session_fail = int(x[18:23])
			session = int(x[0:3])
			break		
		elif tTime[0:9] + str(int(tTime[9:11])-1)+'.59' in x:
			Time = tTime[0:9] + str(int(tTime[9:11])-1)+'.59'
			if "unknown" in x:
				unknown = True
				break
			pre_Time = Time
			try:
				pre_session_fail = int(x[15:20])
			except:
				pre_session_fail = int(x[18:23])
			session = int(x[0:3])
			break
	return pre_Time, pre_session_fail, session, unknown, Time
	
# print result on terminal
def result(cmd,S,P,F,C,R,A,I,T,pt,un,rm):
	if un == True: print(cmd.strip()+" [Done]\n"+colored(pt+"\t[Session: %s] [Build shows unknown] [Run time: %s]"%(S,R), 'yellow'))
	elif rm == True: print(cmd.strip()+" [Done]\n"+colored(pt+"\t[Session: %s] [No modules found] [Run time: %s]"%(S,R), 'yellow'))
	elif C != True:	print(cmd.strip()+" [Done]\n"+colored(pt+"\t[Session: %s] [Not Complete] [Run time: %s]"%(S,R), 'yellow'))
	elif F > 0:	print(cmd.strip()+" [Done]\n"+colored(pt+"\t[Session: %s] [Total Tests: %s] [Passed: %s] [Failed: %s] [Assumption: %s] [Ignored: %s] [Run time: %s]"%(S,T,P,F,A,I,R), 'red'))
	else:	print(cmd.strip()+" [Done]\n"+colored(pt+"\t[Session: %s] [Total Tests: %s] [Passed: %s] [Failed: %s] [Assumption: %s] [Ignored: %s] [Run time: %s]"%(S,T,P,F,A,I,R), 'green'))

# write terminal log
def write(test_suite, time, data):
	if test_suite == 'gsi':
		fw = open(base_path+'android-cts/logs/'+
					str(dt.date.today().year)+'.'+time+'/Terminal_logs', "w")
	else:	
		fw = open(base_path+'android-'+test_suite+'/logs/'+
					str(dt.date.today().year)+'.'+time+'/Terminal_logs', "w")
	fw.write(data)
	fw.close()

# main function
def triage_failure(device, test_suite, cmds):
	global previous_execute_time
	
	# only run one cmd in same second
	while cmds:
		# set dir and cmd for popen use
		if test_suite == 'gsi':
			dir = base_path+"android-cts"
			cmd = "./tools/cts-tradefed run commandAndExit cts-on-gsi "
		elif test_suite == 'sts':
			dir = base_path+"android-"+test_suite
			cmd = "./tools/sts-tradefed run commandAndExit sts-dynamic-full "
		else:
			dir = base_path+"android-"+test_suite
			cmd = "./tools/"+test_suite+"-tradefed run commandAndExit "+test_suite+" "

		current_time = int(round(time.time()))
		if current_time <= previous_execute_time:
			time.sleep(2)
		else:
			previous_execute_time = current_time
			include_filter = cmds[0].strip()
			del cmds[0]
			cmd += include_filter
			log = process([cmd+" -s "+device], dir) # +" --bugreport-on-failure"
			pre_Time = "XXXXXXXXXXXXXXXXX"
			Time = extract_time("I/TestInvocation: Starting invocation for", log)
			session = 0
			pre_session_fail = 0
			unknown = False

			# get session from l r
			if test_suite == 'gsi':
				lr = process(["./tools/cts-tradefed l r"], dir)
			else:
				lr = process(["./tools/"+test_suite+"-tradefed l r"], dir)
			pre_Time, pre_session_fail, session, unknown, Time = get_session(lr, pre_Time, Time, pre_session_fail, session, unknown)
			write(test_suite, Time, log)

			# T = Total P = Pass F = Fail A = Assumption I = Ignored C = Complete 
			T = P = F = A = I = 0
			C = True
			Run_time = ""
			remove = False
			P,F,C,Run_time,A,I,T,remove = status(log,P,F,C,Run_time,A,I,T,remove)
			
			include_filter = include_filter.split()[1].replace('\"','')
			result(include_filter,session,P,F,C,Run_time,A,I,T,pre_Time,unknown,remove)
			
			
			if C == False or F != 0 or unknown == True:
				for i in range(retry_round):
					if test_suite == 'gsi':
						rlog = process(["./tools/cts-tradefed run commandAndExit retry -r "+str(session)+" -s "+device], dir)
					else:
						rlog = process(["./tools/"+test_suite+"-tradefed run commandAndExit retry -r "+str(session)+" -s "+device], dir)
					Time = extract_time("I/TestInvocation: Starting invocation for", rlog)
					unknown = False

					# get session from l r
					if test_suite == 'gsi':
						lr = process(["./tools/cts-tradefed l r"], dir)
					else:
						lr = process(["./tools/"+test_suite+"-tradefed l r"], dir)

					pre_session = session
					pre_Time, pre_session_fail, session, unknown, Time = get_session(lr, pre_Time, Time, pre_session_fail, session, unknown)
					write(test_suite, Time, rlog)

					# T = Total P = Pass F = Fail A = Assumption I = Ignored C = Complete 
					T = P = F = A = I = 0
					C = True
					Run_time = ""
					remove = False
					P,F,C,Run_time,A,I,T,remove = status(rlog,P,F,C,Run_time,A,I,T,remove)
					result(include_filter+" retry",session,P,F,C,Run_time,A,I,T,pre_Time,unknown,remove)

					if C == True and F == 0 and unknown == False:
						break

# set parameters
test_suite = sys.argv[1].lower()
retry_round = 0
if sys.argv[2].isnumeric() == False:
    print("Retry parameter is not numeric!")
    sys.exit()
else:
    retry_round = int(sys.argv[2])
devices = []

s = ""
for i in range(3,len(sys.argv)):
    devices.append(sys.argv[i])
    s += " -s "+sys.argv[i]
	
thread(devices, triage_failure, test_suite, list_cmd())