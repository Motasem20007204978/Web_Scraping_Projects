import socket
from urllib import request
from bs4 import BeautifulSoup as bs

# socket is a module that allows you to create a network connection
# the commands in the socket module are used to create a socket
# 1. create a socket object with socket.socket()
# 2. connect to a server with socket.connect() with port 80
# 3. send encoded url with socket.send()
# 4. receive data with socket.recv() in bytes
# 5. decode data with data.decode()
# 6. close the connection with socket.close()

my_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#create socket
my_soc.connect(('data.pr4e.org', 80))#connect a server
#send a request converted to bytes
my_soc.send('GET HTTP://data.pr4e.org/intro-short.txt HTTP/1.0\r\n\r\n'.encode())

#or
file_data = request.urlopen('HTTP://data.pr4e.org/intro-short.txt')#as 3 rows above

while True:
    data = my_soc.recv(512)#recieve data
    if len(data) < 1:# end of file
        break
    print(data.decode().rstrip())#convert from bytes to text

my_soc.close()
#or 
file_data = file_data.read().decode()
print(file_data)



#url = input('Enter URL: ')
count = int(input('Enter count: '))
pos = int(input('Enter position: '))
#/http://py4e-data.dr-chuck.net/known_by_Kalani.html
looping = 0; names = []
def follow_link(link:str):
    global looping, names  
    looping += 1
    html = request.urlopen(link).read()#read content as bytes
    soup = bs(html, 'html.parser')#read content as html file
    all_a_tags = soup('a')
    link = all_a_tags[pos-1].get('href', None)     
    print('Retrieving: ',link)# None if thers is not a tags 
    names.append(all_a_tags[pos-1].text)
    
    return None if looping == count else follow_link(link)

follow_link('http://py4e-data.dr-chuck.net/known_by_Kalani.html')
print(names[-1])