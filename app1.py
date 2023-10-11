from flask import Flask, request, render_template, redirect, url_for, session, flash, Markup
import time
import os
import subprocess
from flask import Flask, render_template

from flask import Response

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'  # Cambia esto por una clave secreta segura



# Simula una lista de usuarios válidos (esto puede ser una base de datos en la realidad)
usuarios_validos = [
    {"username": "Cisco", "password": "Cisco123!"}
]

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verificar las credenciales
        for user in usuarios_validos:
            if user["username"] == username and user["password"] == password:
                # Si las credenciales son correctas, almacenarlas en la sesión
                session['username'] = username
                return redirect(url_for('INICIO'))  # Redirige a la ruta /inicio

        flash('Credenciales incorrectas. Por favor, inténtalo nuevamente.')

    return render_template('login.html')

#-----------------------------------------------------------#
# Carga los nombres de host desde el archivo myhosts.txt y los almacena en una lista
def cargar_hosts():
    hosts = []
    with open('myhosts', 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("["):
                parts = line.split()
                if parts:
                    host_name = parts[0]
                    hosts.append(host_name)
    return hosts

#---------------------PAGINA DE INICIO-------------------------------------------#
@app.route('/INICIO', methods=['GET', 'POST'])
def INICIO():
    # Carga solo los nombres de host desde el archivo
    hosts = ping_hosts()
    return render_template('inicio.html', hosts=hosts)

def ping_hosts():
    hosts = []
    in_router_section = False  # Bandera para indicar si estamos dentro de la sección [routers]
    
    with open('/etc/hosts', 'r') as hosts_file:
        for line in hosts_file:
            line = line.strip()
            
            if line == '[routers]':
                in_router_section = True
            elif line.startswith('[') and line.endswith(']'):
                in_router_section = False
            elif in_router_section and line:
                host_data = line.split()
                if len(host_data) >= 2:
                    hostname, ip = host_data[1], host_data[0]
                    response = subprocess.run(['ping', '-c', '1', '-W', '1', hostname], stdout=subprocess.PIPE)
                    if response.returncode == 0:
                        status = '<img src = "/static/img/Verde2.png" alt = "Respondiendo" width = "30" height="30">'
                    else:
                        status = '<img src="/static/img/Rojo2.png" alt="No responde" width="30" height="30">'
                    hosts.append({'hostname': hostname, 'ip': ip, 'status': status})
    return hosts





#-----------------------PAGINA DE ALERTAS-----------------------------------------#
@app.route('/ALERTAS')
def ALERTAS():
    return render_template('alertas.html')



#----------------------------------------------------------------#
@app.route('/GESTION')
def GESTION():
    return render_template('gestion.html')

#----------------------------------------------------------------#
from netmiko import ConnectHandler
import json

def conectar_ssh(hostname, puerto, usuario, contraseña):
    dispositivo = {
        'device_type': 'cisco_ios',  # Cambia el tipo de dispositivo según tu necesidad
        'ip': hostname,
        'port': puerto,
        'username': usuario,
        'password': contraseña,
    }
    try:
        ssh = ConnectHandler(**dispositivo)
        return ssh
    except Exception as e:
        return None  # Error en la conexión SSH



@app.route('/SSH', methods=['GET', 'POST'])
def ssh():
    if request.method == 'POST':
        hostname = request.form['hostname']
        puerto = request.form['puerto']
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']

        # Intenta establecer la conexión SSH
        ssh = conectar_ssh(hostname, puerto, usuario, contraseña)
        

        if ssh:
            
            # Realiza operaciones en el servidor SSH y obtén la salida
            # Puedes almacenar la salida en una variable de sesión para mostrarla en la página
            session['ssh'] = ssh
            comando= "sh ip interface brief  | sec Loo"
            with conectar_ssh(hostname, puerto, usuario, contraseña) as conexion_first:
                output = conexion_first.send_command(comando)
                output = json(output)
            return f'La salida del código es: <pre>{output}</pre>'
            #return redirect(url_for('ssh_output'))
        else:
            mensaje_error = 'La autenticación SSH falló. Verifica tus credenciales.'
            return render_template('ssh.html', error=mensaje_error)

    return render_template('ssh.html')








#-----------------------------------------------------------#
@app.route('/AJUSTES', methods=['GET', 'POST'])
def AJUSTES():
    if request.method == 'POST':
        # Obtener los datos del formulario
        gateway = request.form['gateway']
        username = request.form['username']
        password = request.form['password']

        # Guardar la información en un archivo de texto
        with open('credenciales.txt', 'w') as file:
            file.write(f'{gateway}\n')
            file.write(f'{username}\n')
            file.write(f'{password}\n')

    return render_template('ajustes.html')
    

#-----------------------------------------------------------#
@app.route('/ESCANEO', methods=['GET', 'POST'])
def TROUBLESHOOT_EJEC():
    return render_template('escaneo.html')


#-----------------------------------------------------------#
@app.route('/scan')
def scan():
    def generate():
        for i in range(10):  # Ejemplo: realizar alguna tarea durante 10 segundos
            time.sleep(1)  # Simulación de una tarea que lleva tiempo
            yield f'Escaneando... Paso {i + 1}\n'

    return Response(generate(), content_type='text/event-stream')



#-----------------------------------------------------------#
@app.route('/TROUBLESHOOT', methods=['GET', 'POST'])
def TROUBLESHOOT():
    if request.method == 'POST':
        nombre_equipo = request.form['nombre_equipo']
        capa = request.form['capa']

        # Guardar la información en un archivo de texto
        with open('informacion.txt', 'w') as file:
            file.write(f'{nombre_equipo}\n')
            file.write(f'{capa}\n')
            file.write('\n')

    return render_template('tshoot.html')


#-----------------------------------------------------------#
@app.route('/ejecutar_codigo', methods=['POST'])
def ejecutar_codigo():
    # Aquí puedes agregar el código que deseas ejecutar
    # Puedes usar el módulo subprocess para ejecutar comandos de Python
    import subprocess

    # Ejemplo de ejecución de un comando (reemplázalo con tu código real)
    comando = "python3 ejec.py.py"
    resultado = subprocess.run(comando, stdout=subprocess.PIPE, shell=True, text=True)

    # Captura la salida del comando
    salida = resultado.stdout

    return render_template('tshoot.html', salida=salida)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

