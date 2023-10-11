import subprocess

# Leer la información desde el archivo informacion.txt
with open("informacion.txt", "r") as archivo_info:
    lineas = archivo_info.readlines()

# Asegurarse de que el archivo contiene al menos 4 líneas (usuario, contraseña, capa y equipo)
if len(lineas) <= 4:
    capa = lineas[1].strip()
    equipo = lineas[0].strip()
else:
    print("El archivo informacion.txt no contiene la información requerida.")
    exit(1)

# Editar el archivo L1.1.yml con el nombre del host deseado
archivo_playbook = f"L{capa}.yml"
with open(archivo_playbook, "r") as playbook_original:
    lines = playbook_original.readlines()

with open(archivo_playbook, "w") as playbook_modificado:
    for line in lines:
        if line.strip().startswith("hosts:"):
            playbook_modificado.write(f"  hosts: {equipo}\n")
        else:
            playbook_modificado.write(line)

# Comando para ejecutar el playbook de Ansible
comando = f"ansible-playbook {archivo_playbook}"

# Ejecutar el comando y capturar la salida
proceso = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
salida, error = proceso.communicate()

# Mostrar la salida en la consola
print("Salida del playbook:")
print(salida.decode("utf-8"))
print("Errores del playbook:")
print(error.decode("utf-8"))

