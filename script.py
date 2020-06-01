import docker
import psutil
import time
import os
import requests
import sys
class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def writelines(self, datas):
       self.stream.writelines(datas)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)
sys.stdout = Unbuffered(sys.stdout)
docker_id=[]
port=5001
client = docker.from_env()

counter=0

while 1:
	cpuutil=psutil.cpu_percent()
	n = int(cpuutil/10)
	if(cpuutil < 10):
		if(len(client.containers.list()) == 1 ):
			print("Containers = 1 and CPU Utilization is < 10%")
			pass
		elif (len(client.containers.list()) == 0 ):
			print("CPU Utilization < 10% and there are no containers running")
			print("Adding 1 Container")
			container_id=client.containers.run("final-project:latest",  detach=True , ports= {'5000/tcp': port})
			docker_id.append(container_id)
			version= requests.get('http://0.0.0.0:5555/v2/services/haproxy/configuration/defaults',auth=('saadnaeem', '123456'))
			version=str(version.json()['_version'])
			print("haproxy.cfg File version = ",version)
			counter=counter+1;
			nodeName='node'+str(counter)
			addRequest = requests.post('http://0.0.0.0:5555/v2/services/haproxy/configuration/servers?backend=nodes&version='+version, auth=('saadnaeem', '123456'),json={'name':nodeName,'address':'0.0.0.0','port':int(port),'check':'enabled'},headers={'Content-Type':'application/json'})
			print("Response Code from API Call",addRequest.text)
			port=port+1
		else:
			print("CPU Util < 10% and there are more containers than currently required")
			print("Deleting Containers to get to the desired state ....")
			container_id =[]
			for container in client.containers.list():
				(container_id.append(container.id) )
			i=0
			j=len(container_id)
			while(j != 1):
				container = client.containers.get(container_id[i])
				container.stop()
				i=i+1
				nodeName='node'+str(counter)
				print("Testing-->going to delete  cpuutil < 10 and containers are greater than 1")
				version= requests.get('http://0.0.0.0:5555/v2/services/haproxy/configuration/defaults',auth=('saadnaeem', '123456'))
				version=str(version.json()['_version'])
				print("haproxy.cfg File VERSION = ",version)
				deleteRequest = requests.delete('http://0.0.0.0:5555/v2/services/haproxy/configuration/servers/'+nodeName+'?backend=nodes&version='+version, auth=('saadnaeem', '123456'))
				print("Delete API Call Response Code",deleteRequest)
				counter=counter-1
				print("Throttling Deletion Calls to API ..........")
				time.sleep(5)
				j=j-1
	elif (cpuutil > 10):
		print("CPU Util > 10% and already at desired state")
		if(len(client.containers.list()) == n ):
			pass
		elif (len(client.containers.list()) < n ):
			print("CPU Utilization is > 10% and Below Desired State")
			print("Going to add more containers to get to the desired state")
			newCount = n - len(client.containers.list())
			for i in range(newCount):
				container_id=client.containers.run("final-project:latest",  detach=True , ports= {'5000/tcp': port})
				print("Throttling Addition Calls to API ........")
				time.sleep(8)
				version= requests.get('http://0.0.0.0:5555/v2/services/haproxy/configuration/defaults',auth=('saadnaeem', '123456'))
				version=str(version.json()['_version'])
				print("haproxy.cfg VERSION = ",version)
				counter=counter+1;
				nodeName='node'+str(counter)
				addContainer = requests.post('http://0.0.0.0:5555/v2/services/haproxy/configuration/servers?backend=nodes&version='+version, auth=('saadnaeem', '123456'),json={'name':nodeName,'address':'0.0.0.0','port':int(port),'check':'enabled'},headers={'Content-Type':'application/json'})
				print("Node Addition Response Code = ",addContainer.text)
				port=port+1
				print("\n")
				print("Container added ...")  
		elif (len(client.containers.list()) > n ):
			container_id =[]
			for container in client.containers.list():
				(container_id.append(container.id) )
			i=0
			j=len(container_id)
			while(j != 1):
				print("Going to delete containers to get to the desired state")
				container = client.containers.get(container_id[i])
				container.stop()
				i=i+1
				print("Testing-->going to delete  cpuutil > 10 and containers are greater than n")
				nodeName='node'+str(counter)
				version= requests.get('http://0.0.0.0:5555/v2/services/haproxy/configuration/defaults',auth=('saadnaeem', '123456'))
				version=str(version.json()['_version'])
				print(version)
				deleteRequest = requests.delete('http://0.0.0.0:5555/v2/services/haproxy/configuration/servers/'+nodeName+'?backend=nodes&version='+version, auth=('saadnaeem', '123456'))
				print("Delete Request Response Code = ",deleteRequest)
				counter=counter-1
				print("Throttling Deletion Calls to API ........")
				time.sleep(8)
				j=j-1
				print("Deleted 1 Container")  
	print ("CPU Utilization = ",cpuutil)
	time.sleep(8)
	
