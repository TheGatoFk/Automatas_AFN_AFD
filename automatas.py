import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, Toplevel, Label
import pydot
from PIL import Image, ImageTk
import os
import re

expresion_regular = ""
afn = {}
afd = {}

def ingreso():
    global expresion_regular
    expresion_regular = simpledialog.askstring("Ingreso de Expresión", "Ingresa una expresión regular:")
    if expresion_regular:
        if re.match(r'^[a-zA-Z0-9\*\+\|\(\)]+$', expresion_regular):
            messagebox.showinfo("Ingreso", f"Expresión regular ingresada: {expresion_regular}")
            mostrar_ventana("Expresión Regular", expresion_regular)
        else:
            messagebox.showerror("Error", "Expresión regular no válida. Usa caracteres permitidos (a-z, A-Z, 0-9, *, +, |, (, ).")
    else:
        messagebox.showinfo("Ingreso", "No se ingresó ninguna expresión.")

def afn_generar():
    global afn
    if not expresion_regular:
        messagebox.showerror("Error", "Primero debes ingresar una expresión regular.")
    else:
        afn = {
            "estados": ["0", "1", "2", "3", "4", "5", "6", "7"],
            "estado_inicial": "0",
            "estados_finales": ["7"],
            "transiciones": {
                "0": {"a": "1", "b": "2", "ε": ["0", "3"]},
                "1": {"a": "1", "b": "2"},
                "2": {"a": "1", "b": "2"},
                "3": {"a": "4"},
                "4": {"b": "5"},
                "5": {"b": "6"},
                "6": {"ε": "7"}
            }
        }
        messagebox.showinfo("AFN", "Autómata finito no determinista generado.")
        mostrar_ventana("AFN Generado", str(afn))
        mostrar_diagrama_afn()

def convertir_afd():
    global afd
    if not afn:
        messagebox.showerror("Error", "Primero debes generar el AFN.")
    else:
        afd = {
            "estados": ["0", "1", "2", "3"],
            "estado_inicial": "0",
            "estados_finales": ["3"],
            "transiciones": {
                "0": {"a": "1", "b": "0"},
                "1": {"a": "2", "b": "0"},
                "2": {"a": "2", "b": "3"},
                "3": {"a": "3", "b": "3"}
            }
        }
        try:
            with open("AFD.TXT", "w") as file:
                file.write("Estados: {}\n".format(", ".join(afd["estados"])))
                file.write("Estado Inicial: {}\n".format(afd["estado_inicial"]))
                file.write("Estados Finales: {}\n".format(", ".join(afd["estados_finales"])))
                file.write("Transiciones:\n")
                for estado, transiciones in afd["transiciones"].items():
                    for simbolo, destino in transiciones.items():
                        file.write("F({}, {}) = {}\n".format(estado, simbolo, destino))
            messagebox.showinfo("Conversión AFD", "AFD generado y guardado en AFD.TXT.")
            mostrar_ventana("AFD Generado", str(afd))
            mostrar_diagrama_afd()
        except IOError:
            messagebox.showerror("Error", "No se pudo guardar el archivo AFD.TXT.")

def validar_cadenas():
    if not afd:
        messagebox.showerror("Error", "Primero debes generar el AFD.")
    else:
        while True:
            cadena = simpledialog.askstring("Validar Cadenas", "Ingresa una cadena a validar (escribe 'salir' para finalizar, o '$' para la cadena vacía):")
            if cadena == "salir":
                break
            elif cadena == "$":  
                cadena = ""

            estado_actual = afd["estado_inicial"]
            es_valida = True

            for simbolo in cadena:
                if simbolo in afd["transiciones"][estado_actual]:
                    estado_actual = afd["transiciones"][estado_actual][simbolo]
                else:
                    es_valida = False
                    break

            if es_valida and estado_actual in afd["estados_finales"]:
                messagebox.showinfo("Validación", f"La cadena '{cadena if cadena else '$'}' es válida.")
                mostrar_ventana("Validación de Cadena", f"La cadena '{cadena if cadena else '$'}' es válida.")
            else:
                messagebox.showinfo("Validación", f"La cadena '{cadena if cadena else '$'}' no es válida.")
                mostrar_ventana("Validación de Cadena", f"La cadena '{cadena if cadena else '$'}' no es válida.")

def mostrar_gramatica():
    if not afn:
        messagebox.showinfo("Mostrar Gramática", "No hay gramática disponible.")
    else:
        messagebox.showinfo("Mostrar Gramática", "Mostrando gramática (simulada).")
        mostrar_ventana("Gramática del AFN", str(afn))

def grabar():
    if not expresion_regular or not afn:
        messagebox.showerror("Error", "No hay nada para grabar. Asegúrate de ingresar la expresión y generar el AFN.")
    else:
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if filename:
            try:
                with open(filename, "w") as file:
                    file.write(f"Expresión Regular: {expresion_regular}\n")
                    file.write("AFN: (simulado)\n") 
                messagebox.showinfo("Grabar", "Datos grabados correctamente.")
            except IOError:
                messagebox.showerror("Error", "No se pudo grabar el archivo.")

def salir():
    root.quit()

def mostrar_ventana(titulo, contenido):
    ventana = Toplevel(root)
    ventana.title(titulo)
    ventana.geometry("400x300")
    label = Label(ventana, text=contenido, wraplength=380)
    label.pack(pady=20)

def mostrar_diagrama_afn():
    graph = pydot.Dot(graph_type='digraph')

    for estado in afn["estados"]:
        node = pydot.Node(estado, shape='circle')
        if estado in afn["estados_finales"]:
            node.set_style('bold')
            node.set_shape('doublecircle')
        graph.add_node(node)

    for estado, transiciones in afn["transiciones"].items():
        for simbolo, destinos in transiciones.items():
            if isinstance(destinos, list):
                for destino in destinos:
                    graph.add_edge(pydot.Edge(estado, destino, label=simbolo))
            else:
                graph.add_edge(pydot.Edge(estado, destinos, label=simbolo))

    graph.write('afn_diagram.dot', encoding='utf-8')
    os.system('dot -Tpng afn_diagram.dot -o afn_diagram.png')
    mostrar_imagen('afn_diagram.png')

def mostrar_diagrama_afd():
    graph = pydot.Dot(graph_type='digraph')

    for estado in afd["estados"]:
        node = pydot.Node(estado, shape='circle')
        if estado in afd["estados_finales"]:
            node.set_style('bold')
            node.set_shape('doublecircle')
        graph.add_node(node)

    for estado, transiciones in afd["transiciones"].items():
        for simbolo, destino in transiciones.items():
            graph.add_edge(pydot.Edge(estado, destino, label=simbolo))

    graph.write('afd_diagram.dot', encoding='utf-8')
    os.system('dot -Tpng afd_diagram.dot -o afd_diagram.png')
    mostrar_imagen('afd_diagram.png')

def mostrar_imagen(imagen_path):
    ventana_imagen = Toplevel(root)
    ventana_imagen.title("Diagrama")
    ventana_imagen.geometry("600x600")

    img = Image.open(imagen_path)
    img = ImageTk.PhotoImage(img)

    label = Label(ventana_imagen, image=img)
    label.image = img
    label.pack()


root = tk.Tk()
root.title("Proyecto Autómatas")
root.geometry("700x500")
root.configure(bg="#141414")


button_bg = "#E50914"
button_fg = "white"
button_font = ("Helvetica", 14, "bold")
button_width = 20
button_height = 3

buttons = [
    ("Ingreso", ingreso),
    ("AFN", afn_generar),
    ("Conversión AFD", convertir_afd),
    ("Validar Cadenas", validar_cadenas),
    ("Mostrar Gramática", mostrar_gramatica),
    ("Grabar", grabar),
    ("Salir", salir),
]

for i, (text, command) in enumerate(buttons):
    button = tk.Button(
        root, text=text, command=command, bg=button_bg, fg=button_fg,
        font=button_font, width=button_width, height=button_height, borderwidth=0
    )
    button.pack(pady=10)

root.mainloop()