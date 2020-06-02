from django.shortcuts import render
from django.http import HttpResponse, Http404, JsonResponse
from django.core.cache import cache 

import socket
import threading

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP
    
def check_ip(subnet, num):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)  #100 millisecond Timeout
    ip = subnet[:-1] + str(num)
    # print(ip)
    result = sock.connect_ex((ip,82))    
    cache.set('c' + str(num), result)
      
def start_check():
    machine_ip = get_ip()
    k = machine_ip.rfind(".")
    subnet = machine_ip[:k] + '.0'
    machine_num = int(machine_ip[k+1:])
    for num in range(0, 255):
        if num == machine_num:
            cache.set('c' + str(num), None)
            continue
        x = threading.Thread(target=check_ip, args=(subnet,num))
        x.start()
    return(subnet)
        
def get_check():
    st = []
    for num in range(1, 255):
        v = cache.get('c' + str(num))
        if v is None or v != 0:
            continue
        #print(v)
        st.append(num)
    return(st)
        

def index(request):
    return render(request, 'index.html')
       
def check(request):
    subnet = start_check()
    st = get_check()
    #print(st)
    return JsonResponse({'subnet': subnet, 'st': st})

