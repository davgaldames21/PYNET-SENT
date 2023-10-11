import tkinter as tk
from tkinter import scrolledtext, StringVar
import subprocess
import os

def ejecutar_playbook():
    # Obtener la capa y el equipo ingresados por el usuario
    usuario = entrada_usuario.get()
    contraseña = entrada_contraseña.get()
    capa = seleccion_capa.get()
    equipo = entrada_equipo.get()
    
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
    
    # Mostrar la salida en la ventana Tkinter
    ventana_output.insert(tk.END, salida.decode("utf-8"))
    ventana_output.insert(tk.END, error.decode("utf-8"))

ventana = tk.Tk()
ventana.title("Ejecución de Playbook Ansible")


# Etiqueta de bienvenida
etiqueta_bienvenida = tk.Label(ventana, text="Bienvenido a PY-NET-SENTINEL")
etiqueta_bienvenida.pack()

# Etiqueta de bienvenida
etiqueta_bienvenida = tk.Label(ventana, text="Tu asistente para Troubleshooting")
etiqueta_bienvenida.pack()

# Etiqueta y campo de entrada para el usuario
etiqueta_usuario = tk.Label(ventana, text="Ingrese nombre de usuario de los equipos en la red")
etiqueta_usuario.pack()
entrada_usuario = tk.Entry(ventana)
entrada_usuario.pack()

# Etiqueta y campo de entrada para la contraseña
etiqueta_contraseña = tk.Label(ventana, text="Ingrese contraseña de los equipos en la red")
etiqueta_contraseña.pack()
entrada_contraseña = tk.Entry(ventana)
entrada_contraseña.pack()

# Etiqueta y opción de selección para la capa
etiqueta_capa = tk.Label(ventana, text="Seleccione la capa (1, 2 o 3):")
etiqueta_capa.pack()

# Usar OptionMenu para la selección de capa
capas = ["Capa 1 de Acceso", "Capa 2 de Distribución", "Capa 3 de Nucleo"]
seleccion_capa = StringVar()
seleccion_capa.set(capas[0])  # Establecer el valor inicial
opcion_capa = tk.OptionMenu(ventana, seleccion_capa, *capas)
opcion_capa.pack()

# Etiqueta y campo de entrada para el equipo
etiqueta_equipo = tk.Label(ventana, text="Ingrese el nombre del equipo:")
etiqueta_equipo.pack()
entrada_equipo = tk.Entry(ventana)
entrada_equipo.pack()

# Widget de texto desplazable para mostrar la salida
ventana_output = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, width=250, height=35)
ventana_output.pack()

# Botón para ejecutar el playbook
boton_ejecutar = tk.Button(ventana, text="Ejecutar Playbook", command=ejecutar_playbook)
boton_ejecutar.pack()

ventana.mainloop()
