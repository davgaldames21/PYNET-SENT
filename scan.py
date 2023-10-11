from netmiko import *
import sqlite3
import re
import time
import os

equipo_principal= {"ip":"",
"device_type":"cisco_ios",
"username":"",
"password":"",
}
equipo_principal["ip"] =  input ("ingresa la ip Gateway: ")
equipo_principal["username"] =  input ("ingresa el usuario ssh: ")
equipo_principal["password"] =  input ("ingresa tu contraseña ssh: ")

def _exploracion_IP():
    archivo_datos = "sh_intest.txt"
    comando= "sh ip interface brief  | sec Loo"
    with ConnectHandler(**equipo_principal) as conexion_first:
        output = conexion_first.send_command(comando)
        print(type(output))
    with open (archivo_datos, "w") as datos:
        datos.write(output)
    with open (archivo_datos,"r") as ip_:
        IP_encontradas = []
        contenido=ip_.read()
        palabras = contenido.split()          
        name_BaseDatos = str("DB_" + _hostname_device())
        conexion = sqlite3.connect(name_BaseDatos +".db")
        cursor= conexion.cursor()
        for palabra in palabras:
            address_clear = ''.join(c if palabra == 'unassigned' or c == '.' or (c.isdigit() and '.' in palabra) else '' for c in palabra)
            if len(address_clear) >= 7 and len(address_clear) <= 15:
                IP_encontradas.append(address_clear)
        for Direccion in range(len(IP_encontradas)):
            DireccionIP= IP_encontradas[Direccion]
            print(DireccionIP)
            ruta_datos = "ip_host.txt"   
            with open (ruta_datos, "a") as ansible_myhost:
                linea_ansible = (str(DireccionIP)+" "+str(_hostname_device())+"\n")
                ansible_myhost.write(linea_ansible)

            enviar_datos='''
                INSERT INTO '''+ name_BaseDatos+ ''' (DireccionIP)
                VALUES (?)
                '''
            cursor.execute(enviar_datos,(DireccionIP,))
            conexion.commit()

            if DireccionIP == "unassigned":
                pass
            else:
                datos_lo = "sh_iplo.txt"
                with open(datos_lo, "w") as datos:
                    datos.write(DireccionIP)
                    if os.path.exists(datos_lo):
                        os.remove(datos_lo)
        conexion.close()
        if os.path.exists(archivo_datos):
            os.remove(archivo_datos)

def _hostname_device():
    archivo_datos = "sh_device.txt"
    comando = "show running-config | include hostname"
    with ConnectHandler(**equipo_principal) as conexion_first:
        output = conexion_first.send_command(comando)
    with open (archivo_datos, "w") as hostname:
        hostname.write(output)
    with open (archivo_datos,"r")as name_:
        host_read = name_.read()
        name_Devices = host_read.replace('hostname',"")
        name_Devices_ = name_Devices.replace(" ", "")
        name_DB=name_Devices_
    if os.path.exists(archivo_datos):
        os.remove(archivo_datos)
        return name_DB
    

def _Crear_BD(name_DB):
    name_BaseDatos = str("DB_" + name_DB)
    name_BD= str("Bases_datos/"+name_BaseDatos +".db") 
    if os.path.exists(name_DB):
        pass
    else:
        conexion = sqlite3.connect(name_BaseDatos +".db")
        cursor= conexion.cursor()
        creacion_data= '''
            CREATE TABLE IF NOT EXISTS '''+ name_BaseDatos + '''(
                DireccionIP TEXT
            )
            '''
        cursor.execute(creacion_data)
        conexion.commit()
        conexion.close()

def _find_IP_neighbors():
    archivo_datos = "sh_ip_neighbor.txt"
    name_BaseDatos = str("DB_" + _hostname_device())
    conexion = sqlite3.connect(name_BaseDatos +".db")
    cursor= conexion.cursor()
    creacion_new_table= '''
        CREATE TABLE IF NOT EXISTS Neighbors(
            IP_NEIGHBORS TEXT
        )
        '''
    cursor.execute(creacion_new_table)
    conexion.commit()
    name_BaseDatos = str("DB_" + _hostname_device())
    conexion = sqlite3.connect(name_BaseDatos +".db")
    cursor= conexion.cursor()
    comando = "sh cdp entry * | sec IP address"
    with ConnectHandler(**equipo_principal) as conexion_first:
        output = conexion_first.send_command(comando)
    with open (archivo_datos, "w") as hostname:
        hostname.write(output)
    with open (archivo_datos,"r")as name_:
        neighbor_ip = name_.read()
        neighbor_ip_dapurada = re.findall(r'\b[\w.]*\d[\w.]*\b', neighbor_ip)
        neighbors_ip_dapurada = []
        neighbors_ip_dapurada.append (' '.join(neighbor_ip_dapurada))
        ips_depuradas = neighbors_ip_dapurada[0].split()
        print(ips_depuradas)
        for ip_depurada in ips_depuradas:
            enviar_datos='''
                INSERT INTO Neighbors (IP_NEIGHBORS)
                VALUES (?)
                '''
            cursor.execute(enviar_datos,(ip_depurada,))
            conexion.commit()
    if os.path.exists(archivo_datos):
        os.remove(archivo_datos)

def archivos_anisble():
    ruta_datos = "myhost"
    with open (ruta_datos, "a") as ansible_myhost:
        linea_ansible = str(_hostname_device()) + " ansible_user=" + str(equipo_principal["username"]) + " ansible_password=" + str (equipo_principal["password"]+"\n")
        ansible_myhost.write(linea_ansible)

inicio = time.time()
name=_hostname_device()
_Crear_BD(name)
_exploracion_IP()
_find_IP_neighbors()
fin = time.time()
tiempo_transcurrido = fin - inicio
print(f"El tiempo transcurrido fue de {tiempo_transcurrido:.4f} segundos")
    
    

contador_ipsi = 0

name_BaseDatos = str("DB_" + _hostname_device())
conexion = sqlite3.connect(name_BaseDatos +".db")
cursor= conexion.cursor()
consulta_datos = "SELECT IP_NEIGHBORS FROM Neighbors"
cursor.execute(consulta_datos)
resultados = [str(fila[0]) for fila in cursor.fetchall()]
print (resultados)
conexion.close()

def reseteo_tabla_nei():
    name_BaseDatos = str("DB_" + _hostname_device())
    conexion = sqlite3.connect(name_BaseDatos +".db")
    cursor= conexion.cursor()
    consulta_datos = "DELETE FROM Neighbors"
    cursor.execute(consulta_datos)
    conexion.close()

try:
    num_relative = 0
    time_retries = 0
    hostnames = []
    i = 0
    #equipo_principal["ip"] =  resultados[num_relative] 
    while True:
        equipo_principal["ip"] =  resultados[num_relative]
        name=_hostname_device()
        for i in range (len(resultados)):
            if name in hostnames:
                print("saltando dispositivos")
                #num_relative = 1
                reseteo_tabla_nei()
                if time_retries == 3:
                    num_relative = num_relative + 1
                    break
                else:
                    pass
                time_retries = time_retries + 1
                reseteo_tabla_nei()
                print("intentos: " , time_retries)
        
            else:
                if os.path.exists(str("DB_" + _hostname_device()+".db")):
                    reseteo_tabla_nei()
                    pass
                else:
                    pass
                _Crear_BD(name)
                _exploracion_IP()
                _find_IP_neighbors()
                name_BaseDatos = str("DB_" + _hostname_device())
                conexion = sqlite3.connect(name_BaseDatos +".db")
                cursor= conexion.cursor()
                consulta_datos = "SELECT IP_NEIGHBORS FROM Neighbors"
                cursor.execute(consulta_datos)
                resultados = [str(fila[0]) for fila in cursor.fetchall()]
                conexion.close()
                hostnames.append(name)
                print (hostnames)
                archivos_anisble()
                num_relative = 0
                time_retries = 0
#reseteo_tabla_nei()
except:
    num_relative1 = 0
    time_retries1 = 0
    hostnames1 = []
    while True:
        equipo_principal["ip"] =  resultados[num_relative1]
        #print(contador_ipsi)
        name=_hostname_device()
        if name in hostnames1:
            print("saltando dispositivos")
            num_relative1 = 1
            if time_retries1 == 3:
                break
            else:
                pass
            time_retries1 = time_retries1 + 1
            print("intentos: " , time_retries1)
        
        else:
            _Crear_BD(name)
            _exploracion_IP()
            _find_IP_neighbors()
            name_BaseDatos = str("DB_" + _hostname_device())
            conexion = sqlite3.connect(name_BaseDatos +".db")
            cursor= conexion.cursor()
            consulta_datos = "SELECT IP_NEIGHBORS FROM Neighbors"
            cursor.execute(consulta_datos)
            resultados = [str(fila[0]) for fila in cursor.fetchall()]
            conexion.close()
            hostnames1.append(name)
            print (hostnames1)
            archivos_anisble()
            num_relative1 = 0
            time_retries1 = 0
        #print(contador_ipsi)
    
reseteo_tabla_nei()
