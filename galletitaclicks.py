#!/usr/bin/env python3
"""
GalletitaClicks - Aplicación de autoclicks con interfaz gráfica
Funciona en Mac (Intel y ARM)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random
from pynput import mouse
from pynput.mouse import Button
import math
import subprocess
import sys
import platform
import os
import json

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("GalletitaClicks")
        self.root.geometry("400x525")
        self.root.resizable(False, False)
        
        # Variables de estado
        self.is_running = False
        self.click_thread = None
        self.mouse_controller = mouse.Controller()
        self.last_mouse_position = None
        self.mouse_still_time = 0
        self.mouse_still_threshold = 2.0  # Segundos que el mouse debe estar quieto (2 segundos)
        self.last_click_position = None  # Para movimientos suaves
        self.is_smooth_moving = False  # Flag para indicar si hay un movimiento suave en curso
        self.is_startup_routine = False  # Flag para indicar si hay una rutina de inicio en curso
        self.startup_routine_done = False  # Flag para indicar si ya se hizo la rutina de inicio
        # Círculo fijo cuando el mouse está quieto
        self.fixed_circle_center = None  # (x, y) posición del centro del círculo fijo
        self.fixed_circle_radius = None  # Radio del círculo fijo
        # Círculo fijo cuando el mouse está quieto
        self.fixed_circle_center = None  # (x, y) posición del centro del círculo fijo
        self.fixed_circle_radius = None  # Radio del círculo fijo
        
        # Variables de configuración
        # Usar StringVar para poder controlar el formato de 1 decimal
        self.click_interval = tk.StringVar(value="3.0")
        self.use_random_interval = tk.BooleanVar(value=False)
        self.random_interval_max = tk.StringVar(value="3.0")  # Inicializado igual al mínimo cuando se activa
        self.use_random_position = tk.BooleanVar(value=False)
        self.random_radius = tk.IntVar(value=10)
        self.use_smooth_movements = tk.BooleanVar(value=False)
        self.permissions_shown = False  # Flag para indicar si ya se mostró el diálogo de permisos
        
        # Canvas para visualización del círculo
        self.overlay_window = None
        self.overlay_canvas = None
        self.preview_active = False
        self.preview_message_label = None
        
        # Archivo para guardar la configuración (incluye estado de permisos)
        # El directorio home del usuario no requiere permisos especiales para escribir
        self.config_file = os.path.expanduser("~/.galletitaclicks_config.json")
        
        # Cargar configuración guardada
        self.load_config()
        
        self.setup_ui()
        
        # Actualizar widgets después de crear la UI con los valores cargados
        self.update_ui_from_config()
        
        # Configurar guardado automático cuando cambien los valores
        self.setup_auto_save()
        
        # Verificar permisos de accesibilidad al iniciar
        # Usar un delay mayor para asegurar que la ventana esté completamente cargada
        self.root.after(1000, self.check_and_request_permissions)
        
    def setup_ui(self):
        # Estilo moderno
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar fondo lila claro para todos los elementos
        pink_bg = "#F0E5FF"  # Lila pastel
        style.configure("TFrame", background=pink_bg)
        style.configure("TLabel", background=pink_bg)
        style.configure("TCheckbutton", background=pink_bg)
        
        # Intentar cargar el icono de la aplicación
        icon_image = None
        icon_path_found = None
        icon_64_path = None  # Para el icono de 64x64 del .icns
        
        try:
            # Primero intentar extraer 64x64 del .icns (mejor calidad)
            icns_paths = [
                'icon.icns',
                os.path.join(os.path.dirname(__file__), 'icon.icns'),
                os.path.join(os.path.dirname(sys.executable), 'icon.icns'),
            ]
            
            for icns_path in icns_paths:
                if os.path.exists(icns_path):
                    try:
                        # Extraer el tamaño 64x64 del .icns usando sips
                        import tempfile
                        temp_dir = tempfile.mkdtemp()
                        icon_64_path = os.path.join(temp_dir, 'icon_64.png')
                        # Extraer icon_32x32@2x.png que es 64x64
                        result = subprocess.run(
                            ['iconutil', '--convert', 'iconset', '--output', os.path.join(temp_dir, 'temp.iconset'), icns_path],
                            capture_output=True,
                            timeout=5
                        )
                        if result.returncode == 0:
                            # Buscar el archivo de 64x64 (icon_32x32@2x.png)
                            icon_64_file = os.path.join(temp_dir, 'temp.iconset', 'icon_32x32@2x.png')
                            if os.path.exists(icon_64_file):
                                icon_64_path = icon_64_file
                                break
                    except:
                        continue
            
            # Buscar el icono PNG como alternativa
            icon_paths = [
                'icon.png',
                os.path.join(os.path.dirname(__file__), 'icon.png'),
                os.path.join(os.path.dirname(sys.executable), 'icon.png'),
            ]
            
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    try:
                        # Para PNG
                        icon_image = tk.PhotoImage(file=icon_path)
                        # Redimensionar a un tamaño pequeño para el icono de ventana (24x24)
                        small_icon = icon_image.subsample(max(1, icon_image.width() // 24))
                        self.root.iconphoto(True, small_icon)
                        if not icon_path_found:
                            icon_path_found = icon_path
                        break
                    except:
                        continue
        except:
            pass  # Si no se puede cargar el icono, continuar sin él
        
        # Frame principal con fondo rosa claro
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configurar fondo lila claro para la ventana principal
        self.root.configure(bg="#F0E5FF")  # Lila pastel
        main_frame.configure(style="Main.TFrame")
        style.configure("Main.TFrame", background="#F0E5FF")
        
        # Canvas para el icono de fondo en la esquina superior derecha (con margen)
        # Usar el icono de 64x64 del .icns directamente sin redimensionar
        if icon_64_path and os.path.exists(icon_64_path):
            try:
                # Cargar el icono de 64x64 directamente (sin redimensionar)
                bg_icon_image = tk.PhotoImage(file=icon_64_path)
                icon_size = bg_icon_image.width()  # Debería ser 64
                
                # Crear un canvas para el icono de fondo con el tamaño real del icono
                icon_canvas = tk.Canvas(
                    self.root,
                    width=icon_size,
                    height=icon_size,
                    bg="#F0E5FF",
                    highlightthickness=0
                )
                # Posición: 15 píxeles desde arriba y 15 píxeles desde la derecha
                # x = ancho_ventana (400) - tamaño_icono - margen_derecho (15)
                icon_canvas.place(x=400 - icon_size - 35, y=15)
                
                icon_canvas.create_image(icon_size // 2, icon_size // 2, image=bg_icon_image, anchor=tk.CENTER)
                # Guardar referencia para evitar que se elimine
                icon_canvas.bg_icon_image = bg_icon_image
            except Exception as e:
                pass  # Si falla, continuar sin el icono de fondo
        
        # Título (sin icono, solo texto)
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(pady=(0, 20))
        
        title_label = ttk.Label(title_frame, text="GalletitaClicks", font=("Arial", 18, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Tiempo entre clicks
        interval_frame = ttk.Frame(main_frame)
        interval_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(interval_frame, text="Tiempo entre clicks (seg):").pack(anchor=tk.W)
        
        interval_control_frame = ttk.Frame(interval_frame)
        interval_control_frame.pack(fill=tk.X, pady=2)
        
        # Función para formatear el valor a 1 decimal
        def format_interval_entry(event=None):
            try:
                val = float(self.click_interval.get())
                val = round(val, 1)
                # Usar StringVar temporalmente para formatear
                self.click_interval.set(f"{val:.1f}")
                
                # Si el tiempo mínimo es mayor que el máximo, actualizar el máximo
                if self.use_random_interval.get():
                    try:
                        max_val = float(self.random_interval_max.get())
                        if val > max_val:
                            # Actualizar el máximo al valor del mínimo
                            self.random_interval_max.set(f"{val:.1f}")
                            if hasattr(self, 'random_max_scale_var'):
                                self.random_max_scale_var.set(val)
                    except:
                        pass
            except:
                pass
        
        interval_entry = ttk.Entry(interval_control_frame, textvariable=self.click_interval, width=8)
        interval_entry.pack(side=tk.LEFT, padx=(0, 10))
        interval_entry.bind('<FocusOut>', format_interval_entry)
        interval_entry.bind('<Return>', format_interval_entry)
        
        # Función para actualizar el slider con precisión de 1 decimal
        def update_interval_scale(value):
            try:
                val = float(value)
                # Redondear a 1 decimal y formatear
                val = round(val, 1)
                # Formatear a string con 1 decimal para mostrar correctamente
                self.click_interval.set(f"{val:.1f}")
                
                # Si el tiempo mínimo es mayor que el máximo, actualizar el máximo
                if self.use_random_interval.get():
                    try:
                        max_val = float(self.random_interval_max.get())
                        if val > max_val:
                            # Actualizar el máximo al valor del mínimo
                            self.random_interval_max.set(f"{val:.1f}")
                            if hasattr(self, 'random_max_scale_var'):
                                self.random_max_scale_var.set(val)
                    except:
                        pass
            except:
                pass
        
        self.interval_scale = ttk.Scale(
            interval_control_frame,
            from_=0,
            to=120,
            variable=self.click_interval,
            orient=tk.HORIZONTAL,
            length=250,
            command=update_interval_scale
        )
        self.interval_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Random interval - más cerca del tiempo 1
        random_interval_frame = ttk.Frame(main_frame)
        random_interval_frame.pack(fill=tk.X, pady=2)
        
        random_interval_check = ttk.Checkbutton(
            random_interval_frame,
            text="Usar tiempo aleatorio entre dos valores",
            variable=self.use_random_interval,
            command=self.toggle_random_interval
        )
        random_interval_check.pack(anchor=tk.W)
        
        self.random_max_frame = ttk.Frame(main_frame)
        # No empaquetar inicialmente, se mostrará cuando se active el checkbox
        # Guardar referencia al frame del checkbox para posicionamiento
        self.random_interval_frame_ref = random_interval_frame
        
        ttk.Label(self.random_max_frame, text="Tiempo máximo (seg):").pack(anchor=tk.W)
        
        random_max_control_frame = ttk.Frame(self.random_max_frame)
        random_max_control_frame.pack(fill=tk.X, pady=2)
        
        # Función para formatear el valor a 1 decimal y validar que no sea menor al mínimo
        def format_random_max_entry(event=None):
            try:
                val = float(self.random_interval_max.get())
                min_val = float(self.click_interval.get())
                # Asegurar que no sea menor al mínimo
                if val < min_val:
                    val = min_val
                val = round(val, 1)
                self.random_interval_max.set(f"{val:.1f}")
                # Actualizar también el slider si existe
                if hasattr(self, 'random_max_scale_var'):
                    self.random_max_scale_var.set(val)
            except:
                pass
        
        random_max_entry = ttk.Entry(random_max_control_frame, textvariable=self.random_interval_max, width=8)
        random_max_entry.pack(side=tk.LEFT, padx=(0, 10))
        random_max_entry.bind('<FocusOut>', format_random_max_entry)
        random_max_entry.bind('<Return>', format_random_max_entry)
        
        # Función para actualizar el slider con precisión de 1 decimal
        def update_random_max_scale(value):
            try:
                val = float(value)
                # Redondear a 1 decimal y formatear
                val = round(val, 1)
                # Actualizar directamente con formato de 1 decimal
                self.random_interval_max.set(f"{val:.1f}")
            except:
                pass
        
        # Crear una variable DoubleVar para el slider (el slider necesita DoubleVar)
        self.random_max_scale_var = tk.DoubleVar(value=3.0)
        
        # Sincronizar cuando cambia el slider
        def sync_random_max_from_scale(value):
            try:
                val = float(value)
                min_val = float(self.click_interval.get())
                # Asegurar que no sea menor al mínimo
                if val < min_val:
                    val = min_val
                val = round(val, 1)
                self.random_interval_max.set(f"{val:.1f}")
                # Actualizar el slider si se ajustó
                if val != float(value):
                    self.random_max_scale_var.set(val)
            except:
                pass
        
        # Sincronizar cuando cambia el entry
        def sync_random_max_to_scale(*args):
            try:
                val = float(self.random_interval_max.get())
                val = round(val, 1)
                if abs(val - self.random_max_scale_var.get()) > 0.05:
                    self.random_max_scale_var.set(val)
            except:
                pass
        
        self.random_interval_max.trace_add("write", sync_random_max_to_scale)
        
        self.random_max_scale = ttk.Scale(
            random_max_control_frame,
            from_=0,
            to=120,  # Rango fijo de 0 a 120, igual que el tiempo mínimo
            variable=self.random_max_scale_var,
            orient=tk.HORIZONTAL,
            length=250,
            command=sync_random_max_from_scale
        )
        self.random_max_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Random position
        random_pos_frame = ttk.Frame(main_frame)
        random_pos_frame.pack(fill=tk.X, pady=10)
        
        random_pos_check = ttk.Checkbutton(
            random_pos_frame,
            text="Clicks en posición aleatoria alrededor del cursor",
            variable=self.use_random_position,
            command=self.toggle_random_position
        )
        random_pos_check.pack(anchor=tk.W)
        
        self.radius_frame = ttk.Frame(main_frame)
        # No empaquetar inicialmente, se mostrará cuando se active el checkbox
        # Guardar referencia al frame del checkbox para posicionamiento
        self.random_pos_frame_ref = random_pos_frame
        
        ttk.Label(self.radius_frame, text="Radio del círculo (píxeles):").pack(anchor=tk.W)
        
        radius_control_frame = ttk.Frame(self.radius_frame)
        radius_control_frame.pack(fill=tk.X, pady=5)
        
        # Función para formatear el valor a entero
        def format_radius_entry(event=None):
            try:
                val = int(float(self.random_radius.get()))
                if val < 0:
                    val = 0
                elif val > 100:
                    val = 100
                self.random_radius.set(val)
            except:
                self.random_radius.set(10)
        
        radius_entry = ttk.Entry(radius_control_frame, textvariable=self.random_radius, width=8)
        radius_entry.pack(side=tk.LEFT, padx=(0, 10))
        radius_entry.bind('<FocusOut>', format_radius_entry)
        radius_entry.bind('<Return>', format_radius_entry)
        
        # Función para actualizar el slider con incrementos de 1
        def update_radius_scale(value):
            try:
                val = int(float(value))
                if val < 0:
                    val = 0
                elif val > 100:
                    val = 100
                # Asegurar que siempre sea entero
                self.random_radius.set(int(val))
            except:
                pass
        
        self.radius_scale = ttk.Scale(
            radius_control_frame,
            from_=0,
            to=100,
            variable=self.random_radius,
            orient=tk.HORIZONTAL,
            length=200,
            command=update_radius_scale
        )
        self.radius_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Checkbox para movimiento sexy con botón Preview al lado
        smooth_movements_frame = ttk.Frame(self.radius_frame)
        smooth_movements_frame.pack(fill=tk.X, pady=5)
        
        smooth_movements_check = ttk.Checkbutton(
            smooth_movements_frame,
            text="Movimiento sexy",
            variable=self.use_smooth_movements
        )
        smooth_movements_check.pack(side=tk.LEFT, anchor=tk.W)
        
        self.preview_button = ttk.Button(
            smooth_movements_frame,
            text="Preview",
            command=self.toggle_preview,
            style="Preview.TButton",
            width=12  # Mismo ancho que Start/Stop
        )
        self.preview_button.pack(side=tk.RIGHT, padx=(0, 0))
        
        # Mensaje de preview
        self.preview_message_label = ttk.Label(
            self.radius_frame,
            text="",
            font=("Arial", 12, "bold"),
            foreground="blue"
        )
        self.preview_message_label.pack(pady=5)
        
        # Botón de control único (Start/Stop) con estado a la derecha
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        # Botón único Start/Stop con colores (más pequeño)
        # Usar el estilo ya configurado en setup_ui (tema 'clam')
        style = ttk.Style()
        
        # Configurar estilos para Start y Stop con colores suaves
        # El tema 'clam' permite colores de fondo
        # Tonos más suaves y menos radiantes
        style.configure("Start.TButton",
                       font=("Arial", 12, "bold"),
                       foreground="black",
                       background="#81C784",  # Verde más suave
                       borderwidth=1,
                       focuscolor='none',
                       padding=(20, 8))
        style.map("Start.TButton",
                 background=[("active", "#66BB6A"), ("pressed", "#4CAF50")],
                 foreground=[("active", "black")])
        
        style.configure("Stop.TButton",
                       font=("Arial", 12, "bold"),
                       foreground="black",
                       background="#E57373",  # Rojo más suave
                       borderwidth=1,
                       focuscolor='none',
                       padding=(20, 8))
        style.map("Stop.TButton",
                 background=[("active", "#EF5350"), ("pressed", "#E53935")],
                 foreground=[("active", "black")])
        
        # Configurar estilo para el botón Preview
        style.configure("Preview.TButton",
                       font=("Arial", 12, "bold"),
                       foreground="black",
                       background="#ADD8E6",  # Azul claro
                       borderwidth=1,
                       focuscolor='none',
                       padding=(20, 8))  # Padding similar al botón Start/Stop
        style.map("Preview.TButton",
                 background=[("active", "#87CEEB"), ("pressed", "#6BB6FF")],
                 foreground=[("active", "black")])
        
        self.toggle_button = ttk.Button(
            button_frame,
            text="Start",
            command=self.toggle_clicking,
            style="Start.TButton",
            width=12
        )
        self.toggle_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # Estado - a la derecha del botón, alineado a la derecha, con fuente mayor
        self.status_label = ttk.Label(
            button_frame, 
            text="Estado: Detenido", 
            foreground="gray",
            font=("Arial", 18, "normal")
        )
        self.status_label.pack(side=tk.RIGHT, padx=(0, 0))
        
        # Info
        info_label = ttk.Label(
            main_frame,
            text="Nota: Los clicks se pausan cuando mueves el mouse",
            font=("Arial", 11),
            foreground="gray"
        )
        info_label.pack(pady=5)
        
        # Footer (siempre al final)
        footer_label = ttk.Label(
            main_frame,
            text="Made with ❤️ by uborZz for MHS",
            font=("Arial", 12),
            foreground="gray"
        )
        footer_label.pack(side=tk.BOTTOM, pady=(10, 5), anchor=tk.CENTER)
        
    def toggle_random_interval(self):
        if self.use_random_interval.get():
            # Solo cuando se activa el checkbox, establecer el tiempo máximo igual al mínimo
            try:
                min_value = float(self.click_interval.get())
                # Redondear a 1 decimal y establecer igual al mínimo
                max_value = round(min_value, 1)
                self.random_interval_max.set(f"{max_value:.1f}")
                # Actualizar también el slider si existe
                if hasattr(self, 'random_max_scale_var'):
                    self.random_max_scale_var.set(max_value)
            except:
                # Valor por defecto si hay error
                try:
                    default_min = float(self.click_interval.get())
                    self.random_interval_max.set(f"{default_min:.1f}")
                    if hasattr(self, 'random_max_scale_var'):
                        self.random_max_scale_var.set(default_min)
                except:
                    self.random_interval_max.set("1.0")
                    if hasattr(self, 'random_max_scale_var'):
                        self.random_max_scale_var.set(1.0)
            # Mostrar el frame del tiempo máximo después del frame del checkbox
            self.random_max_frame.pack(fill=tk.X, pady=2, after=self.random_interval_frame_ref)
        else:
            # Ocultar el frame del tiempo máximo
            self.random_max_frame.pack_forget()
    
    def toggle_random_position(self):
        if self.use_random_position.get():
            # Mostrar el frame del radio después del frame del checkbox
            self.radius_frame.pack(fill=tk.X, pady=2, after=self.random_pos_frame_ref)
        else:
            # Ocultar el frame del radio
            self.radius_frame.pack_forget()
            self.stop_preview()
    
    def toggle_preview(self):
        """Activa o desactiva la preview del círculo"""
        if self.preview_active:
            self.stop_preview()
        else:
            self.start_preview()
    
    def start_preview(self):
        """Inicia la preview del círculo"""
        if self.preview_active:
            return
        
        try:
            # Obtener el valor actual del radio de la caja de texto
            radius = int(self.random_radius.get())
            # Validar que el radio sea válido (0-100)
            if radius < 0 or radius > 100:
                self.random_radius.set(10)
                radius = 10
        except:
            self.random_radius.set(10)
            radius = 10
        
        self.preview_active = True
        self.preview_message_label.config(text="Preview activa - Clickea para salir de la preview")
        
        # Crear overlay (esto también configurará los bindings de click)
        self.create_overlay()
    
    def stop_preview(self):
        """Detiene la preview del círculo"""
        if not self.preview_active:
            return
        
        self.preview_active = False
        self.preview_message_label.config(text="")
        
        # Destruir overlay
        self.destroy_overlay()
    
    def create_overlay(self):
        """Crea una ventana transparente para mostrar el círculo"""
        if self.overlay_window:
            return
        
        if not self.preview_active and not (self.use_random_position.get() and self.is_running):
            return
        
        try:
            self.overlay_window = tk.Toplevel(self.root)
            self.overlay_window.overrideredirect(True)
            self.overlay_window.attributes("-topmost", True)
            self.overlay_window.attributes("-alpha", 0.6)
            # En macOS, usamos -transparent en lugar de -transparentcolor
            try:
                self.overlay_window.attributes("-transparent", True)
            except:
                pass  # Si no está disponible, continuamos sin transparencia completa
            
            # Usar fondo blanco para mejor visibilidad del círculo
            self.overlay_window.configure(bg="white")
            
            # Obtener tamaño de pantalla
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            self.overlay_window.geometry(f"{screen_width}x{screen_height}+0+0")
            
            self.overlay_canvas = tk.Canvas(
                self.overlay_window,
                width=screen_width,
                height=screen_height,
                highlightthickness=0,
                bg="white"
            )
            self.overlay_canvas.pack(fill=tk.BOTH, expand=True)
            
            # Bind click events al canvas para salir de preview
            if self.preview_active:
                def on_canvas_click(event):
                    if self.preview_active:
                        self.stop_preview()
                
                self.overlay_canvas.bind("<Button-1>", on_canvas_click)
                self.overlay_canvas.bind("<Button-2>", on_canvas_click)
                self.overlay_canvas.bind("<Button-3>", on_canvas_click)
                # También bind a la ventana
                self.overlay_window.bind("<Button-1>", on_canvas_click)
                self.overlay_window.bind("<Button-2>", on_canvas_click)
                self.overlay_window.bind("<Button-3>", on_canvas_click)
            
            # Actualizar posición del círculo periódicamente
            self.update_overlay_position()
        except Exception as e:
            print(f"Error creando overlay: {e}")
            if self.overlay_window:
                try:
                    self.overlay_window.destroy()
                except:
                    pass
                self.overlay_window = None
                self.overlay_canvas = None
    
    def update_overlay_circle(self):
        """Actualiza la posición y tamaño del círculo"""
        if not self.overlay_canvas or not self.overlay_window:
            return
        
        try:
            # Solo mostrar si está en preview o si está activado el random position
            if not self.preview_active and not self.use_random_position.get():
                self.overlay_canvas.delete("all")
                return
                
            self.overlay_canvas.delete("all")
            x, y = self.mouse_controller.position
            
            # Obtener el valor actual del radio de la caja de texto
            try:
                radius = int(self.random_radius.get())
                if radius < 0:
                    radius = 0
                elif radius > 100:
                    radius = 100
            except:
                radius = 10
            
            # Dibujar círculo (las coordenadas del canvas coinciden con las de la pantalla)
            # Círculo exterior más visible
            self.overlay_canvas.create_oval(
                x - radius - 3,
                y - radius - 3,
                x + radius + 3,
                y + radius + 3,
                outline="red",
                width=3,
                tags="circle"
            )
            # Círculo interior más sutil
            self.overlay_canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                outline="orange",
                width=1,
                tags="circle"
            )
        except Exception as e:
            print(f"Error actualizando círculo: {e}")
    
    def update_overlay_position(self):
        """Actualiza la posición del círculo en la ventana overlay"""
        if self.overlay_window and self.overlay_window.winfo_exists():
            # Solo actualizar si está en preview o si está activado el random position durante clicking
            if self.preview_active or (self.use_random_position.get() and self.is_running):
                self.update_overlay_circle()
            self.root.after(30, self.update_overlay_position)
    
    def destroy_overlay(self):
        """Destruye la ventana overlay"""
        if self.overlay_window:
            try:
                self.overlay_window.destroy()
            except:
                pass
            self.overlay_window = None
            self.overlay_canvas = None
    
    def get_click_position(self):
        """Obtiene la posición donde hacer click"""
        # Si es el primer click (last_click_position es None), siempre usar la posición exacta del mouse
        if self.last_click_position is None:
            if self.fixed_circle_center:
                return self.fixed_circle_center
            x, y = self.mouse_controller.position
            return (x, y)
        
        # Para clicks subsiguientes, usar posición aleatoria si está activado
        if self.use_random_position.get() and self.fixed_circle_center and self.fixed_circle_radius is not None and self.fixed_circle_radius > 0:
            # Usar el círculo fijo definido cuando el mouse se detuvo
            center_x, center_y = self.fixed_circle_center
            radius = self.fixed_circle_radius
            
            # Generar posición aleatoria dentro del círculo fijo
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, radius)
            offset_x = int(distance * math.cos(angle))
            offset_y = int(distance * math.sin(angle))
            return (center_x + offset_x, center_y + offset_y)
        
        # Si no hay círculo fijo o el radio es 0, usar la posición del centro del círculo fijo
        if self.fixed_circle_center:
            return self.fixed_circle_center
        
        x, y = self.mouse_controller.position
        return (x, y)
    
    def get_click_interval(self):
        """Obtiene el intervalo de tiempo entre clicks"""
        if self.use_random_interval.get():
            min_interval = float(self.click_interval.get())
            max_interval = float(self.random_interval_max.get())
            return round(random.uniform(min_interval, max_interval), 1)
        return float(self.click_interval.get())
    
    def smooth_move_mouse(self, start_pos, end_pos, duration):
        """Mueve el mouse suavemente de start_pos a end_pos en duration segundos"""
        if start_pos == end_pos:
            return
        
        start_x, start_y = start_pos
        end_x, end_y = end_pos
        
        # Calcular número de pasos (60 pasos por segundo para movimiento suave)
        steps = max(10, int(duration * 60))
        step_duration = duration / steps
        
        # Calcular incrementos
        dx = (end_x - start_x) / steps
        dy = (end_y - start_y) / steps
        
        # Marcar que hay un movimiento suave en curso
        self.is_smooth_moving = True
        
        # Mover el mouse paso a paso
        for i in range(steps + 1):
            if not self.is_running:
                self.is_smooth_moving = False
                break
            
            # Verificar si el usuario movió el mouse manualmente
            try:
                actual_pos = self.mouse_controller.position
                expected_x = int(start_x + dx * i)
                expected_y = int(start_y + dy * i)
                
                # Si la posición real difiere significativamente de la esperada (más de 5 píxeles),
                # significa que el usuario movió el mouse manualmente
                distance = math.sqrt((actual_pos[0] - expected_x)**2 + (actual_pos[1] - expected_y)**2)
                if distance > 5:
                    # Usuario movió el mouse, cancelar movimiento suave
                    self.is_smooth_moving = False
                    return
            except:
                pass
            
            x = int(start_x + dx * i)
            y = int(start_y + dy * i)
            try:
                self.mouse_controller.position = (x, y)
                time.sleep(step_duration)
            except:
                self.is_smooth_moving = False
                break
        
        # Marcar que el movimiento suave terminó
        self.is_smooth_moving = False
    
    def startup_routine(self, center_pos, radius):
        """Realiza la rutina de inicio: espiral-círculo-espiral en 1 segundo"""
        if not self.is_running:
            return False
        
        # Marcar que hay una rutina de inicio en curso
        self.is_startup_routine = True
        
        # Calcular número de puntos para la rutina (60 puntos para 1 segundo a 60 fps)
        total_points = 60
        total_duration = 1.0
        step_duration = total_duration / total_points
        
        center_x, center_y = center_pos
        
        # Dividir en 3 partes: espiral saliente, círculo completo, espiral entrante
        points_per_section = total_points // 3
        
        # Parte 1: Espiral saliente (de centro a radio)
        for i in range(points_per_section):
            if not self.is_running:
                self.is_startup_routine = False
                return False
            
            # Calcular posición esperada
            progress = i / points_per_section
            current_radius = radius * progress
            angle = progress * 2 * math.pi
            expected_x = int(center_x + current_radius * math.cos(angle))
            expected_y = int(center_y + current_radius * math.sin(angle))
            
            # Verificar si el usuario movió el mouse (comparar con posición esperada)
            # Solo verificar después de mover el mouse, no antes
            try:
                self.mouse_controller.position = (expected_x, expected_y)
                # Actualizar last_mouse_position para evitar que el loop detecte esto como movimiento del usuario
                self.last_mouse_position = (expected_x, expected_y)
                time.sleep(step_duration)
                
                # Después de mover, verificar si el usuario movió el mouse manualmente
                current_actual = self.mouse_controller.position
                distance_from_expected = math.sqrt((current_actual[0] - expected_x)**2 + 
                                                  (current_actual[1] - expected_y)**2)
                if distance_from_expected > 20:  # Si está muy lejos de la posición esperada, usuario movió el mouse
                    self.is_startup_routine = False
                    return False
            except:
                self.is_startup_routine = False
                return False
            
        
        # Parte 2: Círculo completo (1 vuelta completa en el radio máximo)
        for i in range(points_per_section):
            if not self.is_running:
                self.is_startup_routine = False
                return False
            
            # Calcular posición esperada
            progress = i / points_per_section
            angle = 2 * math.pi + progress * 2 * math.pi  # Continuar desde donde terminó la espiral
            expected_x = int(center_x + radius * math.cos(angle))
            expected_y = int(center_y + radius * math.sin(angle))
            
            try:
                self.mouse_controller.position = (expected_x, expected_y)
                self.last_mouse_position = (expected_x, expected_y)
                time.sleep(step_duration)
                
                # Después de mover, verificar si el usuario movió el mouse manualmente
                current_actual = self.mouse_controller.position
                distance_from_expected = math.sqrt((current_actual[0] - expected_x)**2 + 
                                                  (current_actual[1] - expected_y)**2)
                if distance_from_expected > 20:
                    self.is_startup_routine = False
                    return False
            except:
                self.is_startup_routine = False
                return False
        
        # Parte 3: Espiral entrante (de radio a centro)
        for i in range(points_per_section):
            if not self.is_running:
                self.is_startup_routine = False
                return False
            
            # Calcular posición esperada
            progress = i / points_per_section
            current_radius = radius * (1 - progress)
            angle = 4 * math.pi + progress * 2 * math.pi
            expected_x = int(center_x + current_radius * math.cos(angle))
            expected_y = int(center_y + current_radius * math.sin(angle))
            
            try:
                self.mouse_controller.position = (expected_x, expected_y)
                self.last_mouse_position = (expected_x, expected_y)
                time.sleep(step_duration)
                
                # Después de mover, verificar si el usuario movió el mouse manualmente
                current_actual = self.mouse_controller.position
                distance_from_expected = math.sqrt((current_actual[0] - expected_x)**2 + 
                                                  (current_actual[1] - expected_y)**2)
                if distance_from_expected > 20:
                    self.is_startup_routine = False
                    return False
            except:
                self.is_startup_routine = False
                return False
        
        # Volver al centro exacto
        try:
            self.mouse_controller.position = center_pos
            self.last_mouse_position = center_pos
            time.sleep(0.01)
        except:
            pass
        
        # Marcar que la rutina terminó
        self.is_startup_routine = False
        return True
    
    def clicking_loop(self):
        """Loop principal de clicking"""
        check_interval = 0.05  # Verificar posición cada 50ms
        
        while self.is_running:
            current_pos = self.mouse_controller.position
            
            # Verificar si el mouse se ha movido
            # Si hay una rutina de inicio en curso, ignorar los movimientos automáticos
            if self.is_startup_routine:
                # Durante la rutina de inicio, solo verificar si el usuario movió el mouse significativamente
                # (esto se hace dentro de la rutina misma)
                time.sleep(check_interval)
                continue
            
            # Si hay un movimiento suave en curso, ignorar los movimientos automáticos
            if self.is_smooth_moving:
                # Durante movimiento suave, solo verificar si el usuario movió el mouse significativamente
                # (esto se hace dentro de smooth_move_mouse)
                time.sleep(check_interval)
                continue
            
            # Verificar si el mouse se ha movido (solo si no hay movimientos automáticos en curso)
            if self.last_mouse_position and current_pos != self.last_mouse_position:
                # Verificar si el movimiento es significativo (más de 5 píxeles)
                # para evitar detectar pequeños ajustes programáticos como movimiento del usuario
                distance = math.sqrt((current_pos[0] - self.last_mouse_position[0])**2 + 
                                   (current_pos[1] - self.last_mouse_position[1])**2)
                
                # Solo resetear si el movimiento es significativo Y no estamos en medio de clicks
                # Si startup_routine_done es True, significa que ya estamos haciendo clicks
                # y los movimientos pequeños pueden ser programáticos
                if distance > 5 and (not self.startup_routine_done or distance > 20):
                    # Este movimiento es del usuario (movimiento significativo)
                    # Mouse se movió, resetear contador y círculo fijo
                    self.last_mouse_position = current_pos
                    self.mouse_still_time = 0
                    self.fixed_circle_center = None
                    self.fixed_circle_radius = None
                    self.last_click_position = None  # Resetear posición de click para movimientos suaves
                    self.startup_routine_done = False  # Resetear para que se vuelva a hacer la rutina
                    time.sleep(check_interval)
                    continue
                else:
                    # Movimiento pequeño, probablemente programático - actualizar last_mouse_position sin resetear
                    self.last_mouse_position = current_pos
            
            # Verificar si el mouse está quieto el tiempo suficiente
            if self.last_mouse_position and current_pos == self.last_mouse_position:
                self.mouse_still_time += check_interval
            else:
                self.mouse_still_time = 0
                self.last_mouse_position = current_pos
            
            # Solo hacer click si el mouse ha estado quieto el tiempo suficiente
            if self.mouse_still_time >= self.mouse_still_threshold:
                # Si no hay círculo fijo definido, definirlo ahora
                if self.fixed_circle_center is None:
                    self.fixed_circle_center = current_pos
                    if self.use_random_position.get():
                        self.fixed_circle_radius = int(self.random_radius.get())
                    else:
                        self.fixed_circle_radius = 0
                    # NO resetear startup_routine_done aquí - solo se resetea al iniciar clicking
                
                # Hacer la rutina de inicio si aún no se ha hecho (solo una vez por sesión)
                if not self.startup_routine_done:
                    # Determinar el radio para la rutina
                    # 5 milímetros = aproximadamente 19 píxeles a 96 DPI
                    # Usar 19 píxeles como radio por defecto mínimo
                    default_radius = 19
                    
                    if self.use_random_position.get() and self.fixed_circle_radius > 0:
                        # Si el radio configurado es menor que el valor por defecto, usar el valor por defecto
                        # para que la rutina sea visual
                        routine_radius = max(self.fixed_circle_radius, default_radius)
                    else:
                        # Usar el valor por defecto
                        routine_radius = default_radius
                    
                    # Realizar la rutina de inicio
                    routine_success = self.startup_routine(self.fixed_circle_center, routine_radius)
                    
                    if routine_success:
                        self.startup_routine_done = True
                    else:
                        # Si la rutina fue cancelada (usuario movió el mouse), resetear todo
                        self.fixed_circle_center = None
                        self.fixed_circle_radius = None
                        self.mouse_still_time = 0
                        self.last_click_position = None
                        self.startup_routine_done = False  # Resetear para que se vuelva a hacer la rutina
                        time.sleep(check_interval)
                        continue
                
                # NO hacer clicks si la rutina aún está en curso
                if self.is_startup_routine:
                    time.sleep(check_interval)
                    continue
                
                # Solo hacer clicks si la rutina ya se completó
                if not self.startup_routine_done:
                    time.sleep(check_interval)
                    continue
                
                try:
                    click_pos = self.get_click_position()
                    interval = self.get_click_interval()
                    move_duration = 0  # Inicializar para uso posterior
                    
                    # Si hay movimientos suaves activados
                    if self.use_smooth_movements.get():
                        # Si hay una posición anterior, usar movimientos suaves
                        if self.last_click_position:
                            # Calcular distancia entre el punto de inicio y el punto final
                            distance = math.sqrt((click_pos[0] - self.last_click_position[0])**2 + 
                                               (click_pos[1] - self.last_click_position[1])**2)
                            
                            # Calcular el diámetro del círculo (2 * radio)
                            # Si hay un círculo fijo con radio, usar ese diámetro
                            if self.fixed_circle_radius and self.fixed_circle_radius > 0:
                                diameter = 2 * self.fixed_circle_radius
                            else:
                                # Si no hay círculo, usar un diámetro por defecto basado en el radio configurado
                                diameter = 2 * int(self.random_radius.get()) if self.random_radius.get() > 0 else 20
                            
                            # Calcular tiempo proporcional: 1 segundo para el diámetro completo
                            # Si la distancia es menor, el tiempo será proporcionalmente menor
                            if diameter > 0:
                                move_duration = (distance / diameter) * 1.0
                            else:
                                move_duration = 0.1  # Valor mínimo si no hay diámetro
                            
                            # Asegurar que no exceda el intervalo entre clicks ni 1 segundo
                            move_duration = min(move_duration, interval, 1.0)
                            # Asegurar un tiempo mínimo razonable (0.05 segundos) para evitar movimientos demasiado rápidos
                            move_duration = max(move_duration, 0.05)
                            
                            # Mover suavemente desde la última posición de click a la nueva
                            self.smooth_move_mouse(self.last_click_position, click_pos, move_duration)
                        else:
                            # Primera vez, mover directamente a la posición de click
                            if self.fixed_circle_center and click_pos != self.fixed_circle_center:
                                self.mouse_controller.position = click_pos
                                time.sleep(0.02)
                        # Actualizar last_mouse_position para que no se detecte como movimiento del usuario
                        self.last_mouse_position = click_pos
                    else:
                        # Mover el mouse a la posición de click si es diferente del centro fijo
                        # Usar el centro fijo como referencia para evitar que el movimiento del mouse
                        # active la detección de movimiento
                        if self.fixed_circle_center and click_pos != self.fixed_circle_center:
                            self.mouse_controller.position = click_pos
                            time.sleep(0.02)  # Pequeña pausa para asegurar que el movimiento se registre
                            # Actualizar last_mouse_position para que no se detecte como movimiento del usuario
                            self.last_mouse_position = click_pos
                    
                    # Hacer click
                    self.mouse_controller.click(Button.left, 1)
                    
                    # Guardar la posición del click para el siguiente movimiento suave
                    self.last_click_position = click_pos
                    
                    # Si usamos movimientos suaves, ya gastamos parte del intervalo en el movimiento
                    # Restar el tiempo usado del intervalo total
                    if self.use_smooth_movements.get() and move_duration > 0:
                        remaining_interval = max(0, interval - move_duration)
                        time.sleep(remaining_interval)
                    else:
                        time.sleep(interval)
                except Exception as e:
                    # Si hay un error de permisos, resetear el flag y mostrar el diálogo
                    error_str = str(e).lower()
                    if 'permission' in error_str or 'accessibility' in error_str or 'trusted' in error_str:
                        # Resetear el flag para que se muestre el diálogo de nuevo
                        self.permissions_shown = False
                        self.save_config()  # Guardar el cambio inmediatamente
                        # Detener el clicking
                        self.is_running = False
                        # Actualizar el estado del botón y la etiqueta en el hilo principal
                        def reset_ui():
                            self.toggle_button.config(
                                text="Start",
                                style="Start.TButton",
                                command=self.start_clicking
                            )
                            self.status_label.config(
                                text="Estado: Detenido", 
                                foreground="red",
                                font=("Arial", 16, "normal")
                            )
                            # Mostrar el diálogo de permisos
                            self.request_accessibility_permissions()
                        self.root.after(0, reset_ui)
                        break
                    else:
                        print(f"Error al hacer click: {e}")
                        import traceback
                        traceback.print_exc()
                    time.sleep(check_interval)
            else:
                # Mouse aún no está quieto el tiempo suficiente
                time.sleep(check_interval)
    
    def toggle_clicking(self):
        """Alterna entre iniciar y detener el clicking"""
        if self.is_running:
            self.stop_clicking()
        else:
            self.start_clicking()
    
    def start_clicking(self):
        """Inicia el proceso de clicking"""
        if self.is_running:
            return
        
        # Verificar permisos antes de iniciar (solo cuando se pulsa Start)
        has_permissions = self.verify_permissions_strict()
        if not has_permissions:
            # Si no hay permisos, resetear el flag para que se muestre el diálogo de nuevo
            # Esto es útil cuando se instala una nueva versión que podría usar config vieja
            self.permissions_shown = False
            self.save_config()  # Guardar el cambio inmediatamente
            
            # Mostrar alerta indicando que la aplicación se cerrará
            message = (
                "GalletitaClicks necesita permisos de accesibilidad para funcionar.\n\n"
                "La aplicación se cerrará ahora. Por favor:\n"
                "1. Vuelve a abrir GalletitaClicks\n"
                "2. Se te pedirá otorgar permisos de accesibilidad\n"
                "3. Ve a Preferencias del Sistema > Privacidad y Seguridad > Privacidad > Accesibilidad\n"
                "4. Marca la casilla junto a GalletitaClicks\n"
                "5. Reinicia la aplicación si es necesario"
            )
            
            messagebox.showinfo(
                "Permisos de Accesibilidad Requeridos",
                message
            )
            
            # Cerrar la aplicación
            self.root.quit()
            self.root.destroy()
            return
        
        self.is_running = True
        self.last_mouse_position = self.mouse_controller.position
        self.mouse_still_time = 0
        # Resetear círculo fijo al iniciar
        self.fixed_circle_center = None
        self.fixed_circle_radius = None
        self.last_click_position = None  # Resetear posición de click anterior
        self.is_smooth_moving = False  # Resetear flag de movimiento suave
        self.is_startup_routine = False  # Resetear flag de rutina de inicio en curso
        self.startup_routine_done = False  # Resetear flag de rutina de inicio
        
        self.click_thread = threading.Thread(target=self.clicking_loop, daemon=True)
        self.click_thread.start()
        
        self.toggle_button.config(
            text="Stop",
            style="Stop.TButton",
            command=self.stop_clicking
        )
        self.status_label.config(
            text="Estado: Activo", 
            foreground="green",
            font=("Arial", 16, "normal")
        )
    
    def stop_clicking(self):
        """Detiene el proceso de clicking"""
        self.is_running = False
        
        if self.click_thread:
            self.click_thread.join(timeout=1.0)
        
        self.toggle_button.config(
            text="Start",
            style="Start.TButton",
            command=self.start_clicking
        )
        self.status_label.config(
            text="Estado: Detenido", 
            foreground="gray",
            font=("Arial", 16, "normal")
        )
    
    def check_and_request_permissions(self):
        """Verifica y solicita permisos de accesibilidad si es necesario"""
        if platform.system() != "Darwin":  # Solo en macOS
            return
        
        # Solo verificar si no se ha mostrado el diálogo antes
        # Si ya se mostró, no verificar al iniciar (se verificará al pulsar Start)
        if not self.permissions_shown:
            # Primera vez, mostrar el diálogo sin verificar (más seguro)
            self.request_accessibility_permissions(update_config=False)
        # Si ya se mostró antes, no hacer nada al iniciar
        # La verificación real se hará cuando el usuario pulse Start
    
    def verify_permissions_strict(self):
        """Verifica permisos de forma estricta intentando mover el mouse"""
        try:
            # Obtener la posición actual del mouse
            original_pos = self.mouse_controller.position
            
            # Intentar mover el mouse a una posición muy cercana (5 píxeles)
            # Si no hay permisos, esto fallará o no moverá el mouse
            test_pos = (original_pos[0] + 5, original_pos[1] + 5)
            
            try:
                # Intentar mover el mouse
                self.mouse_controller.position = test_pos
                time.sleep(0.15)  # Dar más tiempo para que el movimiento se registre
                
                # Verificar la nueva posición
                new_pos = self.mouse_controller.position
                
                # Calcular la distancia entre la posición original y la nueva
                distance_from_original = math.sqrt((new_pos[0] - original_pos[0])**2 + (new_pos[1] - original_pos[1])**2)
                
                # Calcular la distancia entre la posición objetivo y la posición real
                distance_to_target = math.sqrt((new_pos[0] - test_pos[0])**2 + (new_pos[1] - test_pos[1])**2)
                
                # Volver a la posición original
                self.mouse_controller.position = original_pos
                time.sleep(0.05)
                
                # Si el mouse no se movió desde la posición original (distancia < 2 píxeles), no hay permisos
                if distance_from_original < 2:
                    return False
                
                # Si la distancia al objetivo es pequeña (menos de 4 píxeles), el movimiento funcionó
                if distance_to_target < 4:
                    return True
                else:
                    # El mouse se movió pero no al objetivo, podría ser movimiento del usuario
                    # En este caso, asumimos que hay permisos porque el mouse se movió
                    return True
            except Exception as e:
                # Si hay una excepción, probablemente no hay permisos
                error_str = str(e).lower()
                if 'permission' in error_str or 'accessibility' in error_str or 'trusted' in error_str:
                    return False
                # Cualquier otra excepción también indica falta de permisos
                return False
        except Exception as e:
            # Si no podemos ni obtener la posición, definitivamente no hay permisos
            error_str = str(e).lower()
            if 'permission' in error_str or 'accessibility' in error_str or 'trusted' in error_str:
                return False
            return False
    
    def request_accessibility_permissions(self, update_config=True):
        """Muestra un diálogo solicitando permisos de accesibilidad"""
        # Asegurar que la ventana principal esté en primer plano y visible
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.focus_force()
        self.root.update()
        self.root.attributes('-topmost', False)
        
        message = (
            "GalletitaClicks necesita permisos de accesibilidad para controlar el mouse.\n\n"
            "1. Clicka Ok y se abrirán las Preferencias del Sistema\n"
            "2. Marca la casilla junto a esta aplicación\n"
            "3. Reinicia la aplicación después de otorgar los permisos"
        )
        
        result = messagebox.askokcancel(
            "Permisos de Accesibilidad Requeridos",
            message,
            icon="warning"
        )
        
        # Solo marcar permissions_shown si update_config es True
        # Esto permite que al iniciar, si no hay permisos, se muestre el diálogo
        # pero no se marque como "ya mostrado" hasta que realmente se otorguen
        if update_config:
            self.permissions_shown = True
            self.save_config()  # Guardar inmediatamente
        
        if result:
            # Abrir Preferencias del Sistema en la sección de Accesibilidad
            try:
                # En macOS, podemos abrir directamente la sección de Accesibilidad
                subprocess.run([
                    "open",
                    "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
                ])
            except Exception as e:
                # Si falla, intentar abrir las Preferencias del Sistema normalmente
                try:
                    subprocess.run(["open", "/System/Library/PreferencePanes/Security.prefPane"])
                except:
                    messagebox.showinfo(
                        "Abrir Preferencias del Sistema",
                        "Por favor, ve manualmente a:\n"
                        "Preferencias del Sistema > Seguridad y Privacidad > Privacidad > Accesibilidad"
                    )
    
    def load_config(self):
        """Carga la configuración desde el archivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                    # Cargar valores de configuración
                    if 'click_interval' in config:
                        val = round(float(config['click_interval']), 1)
                        self.click_interval.set(f"{val:.1f}")
                    if 'use_random_interval' in config:
                        self.use_random_interval.set(config['use_random_interval'])
                    if 'random_interval_max' in config:
                        val = round(float(config['random_interval_max']), 1)
                        self.random_interval_max.set(f"{val:.1f}")
                    if 'use_random_position' in config:
                        self.use_random_position.set(config['use_random_position'])
                    if 'random_radius' in config:
                        self.random_radius.set(int(config['random_radius']))
                    if 'use_smooth_movements' in config:
                        self.use_smooth_movements.set(config['use_smooth_movements'])
                    
                    # Cargar el estado de permisos
                    self.permissions_shown = config.get('permissions_shown', False)
        except Exception as e:
            # Si hay error al cargar, usar valores por defecto
            print(f"Error al cargar configuración: {e}")
            pass
    
    def update_ui_from_config(self):
        """Actualiza los widgets de la UI con los valores cargados"""
        try:
            # Usar after para asegurar que todos los widgets estén creados
            self.root.after(100, self._do_update_ui_from_config)
        except Exception as e:
            print(f"Error al programar actualización de UI: {e}")
            pass
    
    def _do_update_ui_from_config(self):
        """Actualiza los widgets de la UI con los valores cargados (ejecutado después de crear la UI)"""
        try:
            # Actualizar slider del tiempo máximo con el valor cargado
            if hasattr(self, 'random_max_scale_var'):
                try:
                    val = float(self.random_interval_max.get())
                    self.random_max_scale_var.set(val)
                except:
                    pass
            
            # Activar checkboxes y mostrar frames correspondientes si están marcados
            # Usar las funciones toggle para asegurar que todo se configure correctamente
            if self.use_random_interval.get():
                # Llamar a toggle para mostrar el frame y configurar valores
                if hasattr(self, 'random_max_frame'):
                    self.random_max_frame.pack(fill=tk.X, pady=2, after=self.random_interval_frame_ref)
                    # Asegurar que el slider esté sincronizado
                    try:
                        val = float(self.random_interval_max.get())
                        if hasattr(self, 'random_max_scale_var'):
                            self.random_max_scale_var.set(val)
                    except:
                        pass
            
            if self.use_random_position.get():
                # Llamar a toggle para mostrar el frame
                if hasattr(self, 'radius_frame'):
                    self.radius_frame.pack(fill=tk.X, pady=5, after=self.random_pos_frame_ref)
        except Exception as e:
            print(f"Error al actualizar UI desde configuración: {e}")
            import traceback
            traceback.print_exc()
            pass
    
    def save_config(self):
        """Guarda la configuración en el archivo"""
        try:
            config = {
                'click_interval': float(self.click_interval.get()),
                'use_random_interval': self.use_random_interval.get(),
                'random_interval_max': float(self.random_interval_max.get()),
                'use_random_position': self.use_random_position.get(),
                'random_radius': self.random_radius.get(),
                'use_smooth_movements': self.use_smooth_movements.get(),
                'permissions_shown': getattr(self, 'permissions_shown', False)
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error al guardar configuración: {e}")
            pass
    
    def setup_auto_save(self):
        """Configura el guardado automático cuando cambien los valores"""
        def on_change(*args):
            # Guardar después de un pequeño delay para evitar guardar demasiado frecuentemente
            self.root.after(500, self.save_config)
        
        # Configurar trace para guardar cuando cambien los valores
        self.click_interval.trace_add("write", on_change)
        self.use_random_interval.trace_add("write", on_change)
        self.random_interval_max.trace_add("write", on_change)
        self.use_random_position.trace_add("write", on_change)
        self.random_radius.trace_add("write", on_change)
        self.use_smooth_movements.trace_add("write", on_change)
    
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        # Guardar configuración antes de cerrar
        self.save_config()
        self.stop_clicking()
        self.stop_preview()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = AutoClicker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()

