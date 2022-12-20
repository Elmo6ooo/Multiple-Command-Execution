#!/usr/bin/python3
import os
import sys
import datetime as dt
from termcolor import colored
	
#get specific line
def select_line(string, line_index):
    return string.splitlines()[line_index]
    
#get data from log
def status(log):
	global P,F,C,Run_time,A,I,T,remove
	for x in range(-30,0): 
		tmp = select_line(log, x)
		if "PASSED            :" in tmp:	P = int(tmp[20:])
		elif "FAILED            :" in tmp:	F = int(tmp[20:]) 
		elif "ASSUMPTION_FAILURE:" in tmp: A = int(tmp[20:])
		elif "Total Tests" in tmp:	T = int(tmp[20:])
		elif "IGNORED           :" in tmp: I = int(tmp[20:])
		elif "IMPORTANT" in tmp:	C = False
		elif "Total Run time" in tmp:	Run_time = tmp[16:]
		elif "No modules found matching" in tmp:	remove = True

#extract results time
def extract_time(log):
    global Time
    for x in range(20):
        tmp = select_line(log, x)
        if "I/TestInvocation: Starting invocation for" in tmp:
            Time = tmp[0:14]
            break
    Time = Time.replace(Time[2], '.').replace(Time[5],'_').replace(':','.')	

# get results session
def get_session(log, T, first_round):
	global pre_Time, pre_session_fail, session, unknown, Time
	for x in log.splitlines():
		#inscase new result worst than previous, consider multiple machine running
		tmp = 0
		if pre_Time in x:
			tmp = int(x[0:3])

		#first round
		if first_round:
			if T in x:
				if "unknown" in x:
					unknown = True
					break
				pre_Time = T
				try:
					pre_session_fail = int(x[15:20])
				except:
					pre_session_fail = int(x[18:23])
				session = int(x[0:3])
				break
			elif T[0:12]+'09' in x:
				Time = T[0:12]+'09'
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
			elif T[0:13]+str(int(T[13])-1) in x:
				Time = T[0:13]+str(int(Time[13])-1)
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
			elif T[0:12] + str(int(T[-2:])-1) in x:
				Time = T[0:12] + str(int(T[-2:])-1)
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
			elif T[0:9] + str(int(T[9:11])-1)+'.59' in x:
				Time = T[0:9] + str(int(T[9:11])-1)+'.59'
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
		#other
		else:
			if T in x:
				if "unknown" in x:
					unknown = True
					break
				new_session_fail = int(x[16:20])
				if(new_session_fail < pre_session_fail):
					pre_Time = T
					pre_session_fail = new_session_fail
					session = int(x[0:3])
					break
				else:
					session = tmp
					break
			elif T[0:12]+'09' in x:
				Time = T[0:12]+'09'
				if "unknown" in x:
					unknown = True
					break
				new_session_fail = int(x[16:20])
				if(new_session_fail < pre_session_fail):
					pre_Time = Time
					pre_session_fail = new_session_fail
					session = int(x[0:3])
					break
				else:
					session = tmp
					break
			elif T[0:13]+str(int(T[13])-1) in x:
				Time = T[0:13]+str(int(T[13])-1)
				if "unknown" in x:
					unknown = True
					break
				new_session_fail = int(x[16:20])
				if(new_session_fail < pre_session_fail):
					pre_Time = Time
					pre_session_fail = new_session_fail
					session = int(x[0:3])
					break
				else:
					session = tmp
					break
			elif T[0:12] + str(int(T[-2:])-1) in x:
				Time = T[0:12] + str(int(T[-2:])-1)
				if "unknown" in x:
					unknown = True
					break
				new_session_fail = int(x[16:20])
				if(new_session_fail < pre_session_fail):
					pre_Time = Time
					pre_session_fail = new_session_fail
					session = int(x[0:3])
					break
				else:
					session = tmp
					break
			elif T[0:9] + str(int(T[9:11])-1)+'.59' in x:
				Time = T[0:9] + str(int(T[9:11])-1)+'.59'
				if "unknown" in x:
					unknown = True
					break
				new_session_fail = int(x[16:20])
				if(new_session_fail < pre_session_fail):
					pre_Time = Time
					pre_session_fail = new_session_fail
					session = int(x[0:3])
					break
				else:
					session = tmp
					break

#print result on terminal
def result(cmd,S,P,F,C,R,A,I,T,pt,un,rm):
	if un == True: print(cmd.strip()+" [Done]\n"+colored(pt+"\t[Session: %s] [Build shows unknown] [Run time: %s]"%(S,R), 'yellow'))
	elif rm == True: print(cmd.strip()+" [Done]\n"+colored(pt+"\t[Session: %s] [No modules found] [Run time: %s]"%(S,R), 'yellow'))
	elif C != True:	print(cmd.strip()+" [Done]\n"+colored(pt+"\t[Session: %s] [Not Complete] [Run time: %s]"%(S,R), 'yellow'))
	elif F > 0:	print(cmd.strip()+" [Done]\n"+colored(pt+"\t[Session: %s] [Total Tests: %s] [Passed: %s] [Failed: %s] [Assumption: %s] [Ignored: %s] [Run time: %s]"%(S,T,P,F,A,I,R), 'red'))
	else:	print(cmd.strip()+" [Done]\n"+colored(pt+"\t[Session: %s] [Total Tests: %s] [Passed: %s] [Failed: %s] [Assumption: %s] [Ignored: %s] [Run time: %s]"%(S,T,P,F,A,I,R), 'green'))

#write terminal log
def write(time, data):
	if Mode == 'gsi':
		fw = open('/usr/local/google/home/chienliu/Downloads/android-cts/logs/'+str(dt.date.today().year)+'.'+time+'/Terminal_logs', "w")
	else:
		fw = open("/usr/local/google/home/chienliu/Downloads/android-"+Mode+"/logs/"+str(dt.date.today().year)+'.'+time+'/Terminal_logs', "w")
	fw.write(data)
	fw.close()

#check parameters and set parameters
mode = ''
retry_round = 0
serial_num = []
if sys.argv[1].lower() == False:
    print("Mode parameter is not lowercase!")
    sys.exit()
else:
    Mode = sys.argv[1]

if sys.argv[2].isnumeric() == False:
    print("Retry parameter is not numeric!")
    sys.exit()
else:
    retry_round = int(sys.argv[2])

s = ""
for i in range(3,len(sys.argv)):
    serial_num.append(sys.argv[i])
    s += " -s "+sys.argv[i]
	
#open cmd file and keep each command in cmd[]
cmd = []
fr = open("cmd", "r")
for i in fr:
	cmd.append(i)
	
#cd to dir
if Mode == 'gsi':
    os.chdir("/usr/local/google/home/chienliu/Downloads/android-cts/tools")
else:
    os.chdir("/usr/local/google/home/chienliu/Downloads/android-"+Mode+"/tools")

#execute each command
for i in range(len(cmd)):
	if cmd[i] == '\n':
		continue
	else:
		if Mode == 'gsi':
			p = os.popen("./cts-tradefed run commandAndExit cts-on-gsi "+cmd[i].strip()+s)
		elif Mode == 'sts':
			p = os.popen("./sts-tradefed run commandAndExit sts-dynamic-full "+cmd[i].strip()+s)
		else:
			p = os.popen("./"+Mode+"-tradefed run commandAndExit "+Mode+" "+cmd[i].strip()+s)
		log = p.read()

		pre_Time = "XXXXXXXXXXXXXXXXX"
		Time = ""
		extract_time(log)

		session = 0
		pre_session_fail = 0
		unknown = False

		#get session from l r
		if Mode == 'gsi':
			p = os.popen("./cts-tradefed l r")
		else:
			p = os.popen("./"+Mode+"-tradefed l r")

		get_session(p.read(), Time, True)
		write(Time,log)
		#T = Total P = Pass F = Fail A = Assumption I = Ignored C = Complete 
		T = P = F = A = I = 0
		C = True
		Run_time = ""
		remove = False
		status(log)
		result(cmd[i],session,P,F,C,Run_time,A,I,T,pre_Time,unknown,remove)
		
		
		if C == False or F != 0 or unknown == True:
			for i in range(retry_round):
				if Mode == 'gsi':
					p = os.popen("./cts-tradefed run commandAndExit retry -r "+str(session)+s)
				else:
					p = os.popen("./"+Mode+"-tradefed run commandAndExit retry -r "+str(session)+s)
				rlog = p.read()

				extract_time(rlog)
				unknown = False

				#get session from l r
				if Mode == 'gsi':
					p = os.popen("./cts-tradefed l r")
				else:
					p = os.popen("./"+Mode+"-tradefed l r")

				pre_session = session
				get_session(p.read(), Time, True)
				write(Time,rlog)

				#T = Total P = Pass F = Fail A = Assumption I = Ignored C = Complete 
				T = P = F = A = I = 0
				C = True
				Run_time = ""
				remove = False
				status(rlog)
				result("run retry -r "+str(pre_session),session,P,F,C,Run_time,A,I,T,pre_Time,unknown,remove)

				if C == True and F == 0 and unknown == False:
					break
					
	
