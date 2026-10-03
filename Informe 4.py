import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import threading

class VehiculoBase:
    """Clase base para representar las propiedades de un competidor."""
    def __init__(self, id_vehiculo, color):
        self.id_vehiculo = id_vehiculo
        self.color = color
        self.pos_x = 50.0
        self.direccion = 1  
        self.rondas_completadas = 0
        self.tiempo_total = 0.0
        self.finalizado = False
        self.intervalo = random.uniform(0.01, 0.05)  

    def cambiar_velocidad_aleatoria(self):
        """Cambia el intervalo del temporizador de forma aleatoria al tocar un extremo."""
        self.intervalo = random.uniform(0.008, 0.04)


class AutoCarrera(VehiculoBase):
    """Subclase que hereda de VehiculoBase e integra la representación gráfica."""
    def __init__(self, id_vehiculo, color, canvas, y_pos):
        super().__init__(id_vehiculo, color)
        self.canvas = canvas
        self.y_pos = y_pos
        self.dibujar_vehiculo()

    def dibujar_vehiculo(self):
        """Dibuja el auto en el Canvas (Cuerpo, techo, ruedas y número)."""
        x = self.pos_x
        y = self.y_pos
        
       
        self.chasis = self.canvas.create_rectangle(x, y, x + 40, y + 15, fill=self.color, outline="black", width=2)
        
        self.techo = self.canvas.create_rectangle(x + 10, y - 8, x + 30, y, fill="lightgray", outline="black")
        
        self.rueda1 = self.canvas.create_oval(x + 5, y + 12, x + 13, y + 20, fill="black")
        self.rueda2 = self.canvas.create_oval(x + 27, y + 12, x + 35, y + 20, fill="black")
        
        self.texto_id = self.canvas.create_text(x + 20, y + 7, text=str(self.id_vehiculo), fill="white", font=("Arial", 9, "bold"))

    def mover_a(self, nueva_x):
        """Actualiza la posición gráfica de todas las partes del vehículo."""
        dx = nueva_x - self.pos_x
        self.pos_x = nueva_x
        self.canvas.move(self.chasis, dx, 0)
        self.canvas.move(self.techo, dx, 0)
        self.canvas.move(self.rueda1, dx, 0)
        self.canvas.move(self.rueda2, dx, 0)
        self.canvas.move(self.texto_id, dx, 0)



class CarreraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Laboratorio 4 - Competencia Automovilística (10 Vehículos)")
        self.root.geometry("1050x780")
        self.root.resizable(False, False)

        self.num_vehiculos = 10
        self.colores = ["#E74C3C", "#3498DB", "#2ECC71", "#F1C40F", "#9B59B6", 
                        "#E67E22", "#1ABC9C", "#34495E", "#D35400", "#7F8C8D"]
        
        self.autos = []
        self.hilos = []
        self.tiempos_llegada = []
        self.carrera_activa = False
        self.tiempo_inicio = 0.0

        self.crear_interfaz()

    def crear_interfaz(self):
        
        frame_control = tk.LabelFrame(self.root, text=" Configuración de la Carrera ", font=("Arial", 11, "bold"), padx=10, pady=10)
        frame_control.pack(fill="x", padx=15, pady=10)

    
        tk.Label(frame_control, text="Apueste por un auto (1-10):", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.spn_apuesta = ttk.Spinbox(frame_control, from_=1, to=10, width=5, state="readonly")
        self.spn_apuesta.set(1)
        self.spn_apuesta.grid(row=0, column=1, padx=5, pady=5)

        
        tk.Label(frame_control, text="Número de Rondas (Ida y Vuelta):", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.spn_rondas = ttk.Spinbox(frame_control, from_=1, to=10, width=5, state="readonly")
        self.spn_rondas.set(2)
        self.spn_rondas.grid(row=0, column=3, padx=5, pady=5)

      
        tk.Label(frame_control, text="Velocidad del Tiempo General:", font=("Arial", 10)).grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.slider_velocidad = tk.Scale(frame_control, from_=0.2, to=3.0, resolution=0.1, orient="horizontal", length=130)
        self.slider_velocidad.set(1.0) # 1.0 es velocidad normal
        self.slider_velocidad.grid(row=0, column=5, padx=5, pady=5)

       
        self.btn_iniciar = tk.Button(frame_control, text="Iniciar Carrera", bg="#27AE60", fg="white", font=("Arial", 10, "bold"), command=self.iniciar_carrera)
        self.btn_iniciar.grid(row=0, column=6, padx=10, pady=5)

        self.btn_reiniciar = tk.Button(frame_control, text="Reiniciar", bg="#C0392B", fg="white", font=("Arial", 10, "bold"), command=self.reiniciar_carrera, state="disabled")
        self.btn_reiniciar.grid(row=0, column=7, padx=5, pady=5)

        
        frame_pista = tk.Frame(self.root, bd=2, relief="sunken")
        frame_pista.pack(padx=15, pady=5)

        self.canvas_ancho = 1010
        self.canvas_alto = 380
        self.canvas = tk.Canvas(frame_pista, width=self.canvas_ancho, height=self.canvas_alto, bg="#2C3E50")
        self.canvas.pack()

        self.inicializar_pista_y_autos()

    
        frame_inferior = tk.Frame(self.root)
        frame_inferior.pack(fill="both", expand=True, padx=15, pady=5)

   
        self.lbl_resultado = tk.Label(frame_inferior, text="¡Realice su apuesta y presione 'Iniciar Carrera'!", font=("Arial", 11, "bold"), fg="#2980B9")
        self.lbl_resultado.pack(pady=3)

       
        columnas = ("Posicion", "Vehiculo", "TiempoTotal", "Rondas")
        self.tabla_pos = ttk.Treeview(frame_inferior, columns=columnas, show="headings", height=8)
        
        self.tabla_pos.heading("Posicion", text="Posición")
        self.tabla_pos.heading("Vehiculo", text="Vehículo (Auto #)")
        self.tabla_pos.heading("TiempoTotal", text="Tiempo Total (s)")
        self.tabla_pos.heading("Rondas", text="Rondas Completadas")

        self.tabla_pos.column("Posicion", anchor="center", width=120)
        self.tabla_pos.column("Vehiculo", anchor="center", width=200)
        self.tabla_pos.column("TiempoTotal", anchor="center", width=220)
        self.tabla_pos.column("Rondas", anchor="center", width=220)

        self.tabla_pos.pack(fill="both", expand=True)

    def inicializar_pista_y_autos(self):
        """Dibuja carriles, líneas de salida/meta e instancia los 10 vehículos."""
        self.canvas.delete("all")
        self.autos.clear()

        linea_salida_x = 50
        linea_meta_x = self.canvas_ancho - 50

       
        self.canvas.create_line(linea_salida_x, 0, linea_salida_x, self.canvas_alto, fill="white", width=3, dash=(4, 4))
        self.canvas.create_line(linea_meta_x, 0, linea_meta_x, self.canvas_alto, fill="yellow", width=4)

       
        alto_carril = self.canvas_alto / self.num_vehiculos
        for i in range(self.num_vehiculos):
            y_pos = (i * alto_carril) + (alto_carril / 2) - 5
            
            if i > 0:
                self.canvas.create_line(0, i * alto_carril, self.canvas_ancho, i * alto_carril, fill="#5D6D7E", dash=(2, 2))
            
            auto = AutoCarrera(id_vehiculo=i+1, color=self.colores[i], canvas=self.canvas, y_pos=y_pos)
            self.autos.append(auto)

    def rutina_hilo_vehiculo(self, auto, total_rondas):
        """Rutina independiente para el temporizador de cada vehículo (1 hilo por auto)."""
        limite_izq = 50
        limite_der = self.canvas_ancho - 90
        paso_base = 5

        while self.carrera_activa and auto.rondas_completadas < total_rondas:
           
            factor_escala = float(self.slider_velocidad.get())
            tiempo_espera = auto.intervalo / factor_escala

            time.sleep(tiempo_espera)

            if not self.carrera_activa:
                break

            nueva_x = auto.pos_x + (paso_base * auto.direccion)

          
            if nueva_x >= limite_der and auto.direccion == 1:
                nueva_x = limite_der
                auto.direccion = -1  # Cambia a sentido Vuelta
                auto.cambiar_velocidad_aleatoria()  

            
            elif nueva_x <= limite_izq and auto.direccion == -1:
                nueva_x = limite_izq
                auto.direccion = 1  # Cambia a sentido Ida
                auto.rondas_completadas += 1
                auto.cambiar_velocidad_aleatoria()  

            
            self.root.after(0, auto.mover_a, nueva_x)

       
        if self.carrera_activa and auto.rondas_completadas >= total_rondas and not auto.finalizado:
            auto.finalizado = True
            tiempo_final = round(time.time() - self.tiempo_inicio, 3)
            auto.tiempo_total = tiempo_final
            self.root.after(0, self.registrar_llegada, auto)

    def registrar_llegada(self, auto):
        """Registra la llegada de cada auto y actualiza la tabla."""
        self.tiempos_llegada.append(auto)
        
        if len(self.tiempos_llegada) == 1:
            auto_apostado = int(self.spn_apuesta.get())
            if auto.id_vehiculo == auto_apostado:
                self.lbl_resultado.config(text=f"¡FELICITACIONES! Ganó el Auto #{auto.id_vehiculo}. ¡Ganaste tu apuesta! 🎉", fg="#27AE60")
            else:
                self.lbl_resultado.config(text=f"El Ganador fue el Auto #{auto.id_vehiculo}. Tu auto (#{auto_apostado}) no ganó. ❌", fg="#C0392B")

        self.actualizar_tabla_posiciones()

        if len(self.tiempos_llegada) == self.num_vehiculos:
            self.carrera_activa = False

    def actualizar_tabla_posiciones(self):
        """Limpia y vuelve a llenar la tabla ordenada por tiempo de menor a mayor."""
        for item in self.tabla_pos.get_children():
            self.tabla_pos.delete(item)

        autos_ordenados = sorted(self.tiempos_llegada, key=lambda x: x.tiempo_total)

        for pos, auto in enumerate(autos_ordenados, start=1):
            self.tabla_pos.insert("", "end", values=(
                f"#{pos}",
                f"Auto #{auto.id_vehiculo}",
                f"{auto.tiempo_total:.3f} s",
                f"{auto.rondas_completadas}"
            ))

    def iniciar_carrera(self):
        """Inicia los 10 temporizadores/hilos independientes."""
        self.carrera_activa = True
        self.tiempos_llegada.clear()
        self.tiempo_inicio = time.time()

        self.btn_iniciar.config(state="disabled")
        self.spn_apuesta.config(state="disabled")
        self.spn_rondas.config(state="disabled")
        self.btn_reiniciar.config(state="normal")
        self.lbl_resultado.config(text="¡Carrera en progreso! Los temporizadores están activos...", fg="#E67E22")

        total_rondas = int(self.spn_rondas.get())

        self.hilos = []
        for auto in self.autos:
            hilo = threading.Thread(target=self.rutina_hilo_vehiculo, args=(auto, total_rondas), daemon=True)
            self.hilos.append(hilo)
            hilo.start()

    def reiniciar_carrera(self):
        """Detiene los hilos actuales y restablece la GUI para una nueva carrera."""
        self.carrera_activa = False  

        for item in self.tabla_pos.get_children():
            self.tabla_pos.delete(item)

        self.inicializar_pista_y_autos()

        self.btn_iniciar.config(state="normal")
        self.spn_apuesta.config(state="readonly")
        self.spn_rondas.config(state="readonly")
        self.btn_reiniciar.config(state="disabled")
        self.lbl_resultado.config(text="¡Carrera reiniciada! Haga sus apuestas para el nuevo juego.", fg="#2980B9")

if __name__ == "__main__":
    root = tk.Tk()
    app = CarreraApp(root)
    root.mainloop()