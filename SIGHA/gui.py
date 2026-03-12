import customtkinter as ctk
from datetime import datetime
try:
    from data_base import *
except ImportError:
    print("Error: No se encontró data_base.py en la misma carpeta.")

class AppSIGHA(ctk.CTk):
    def __init__(self):
        super().__init__()
        try:
            inicializar_db()
        except Exception as e:
            print(f"Error al iniciar DB: {e}")

        self.title("SIGHA V0.5 | Facturación Hídrica")
        self.geometry("1200x800")
        
        # Grid Principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#1a1c1e")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="💧 SIGHA", font=("Segoe UI", 32, "bold"), text_color="#3b8ed0").pack(pady=(40, 10))
        
        # Botones
        self.btn_f = self.create_btn("📝 Facturación", self.switch_to_factura)
        self.btn_b = self.create_btn("🔍 Historial", self.switch_to_buscar)
        self.btn_l = self.create_btn("📋 Lista Global", self.switch_to_lista)
        
        self.btn_ref = ctk.CTkButton(self.sidebar, text="🔄 REFRESCAR", command=self.refrescar_todo)
        self.btn_ref.pack(side="bottom", pady=20, padx=20)

        # --- VISTAS ---
        self.view_facturacion = ctk.CTkFrame(self, fg_color="transparent")
        self.view_busqueda = ctk.CTkFrame(self, fg_color="transparent")
        self.view_lista_total = ctk.CTkFrame(self, fg_color="transparent")

        self.init_facturacion_ui()
        self.init_busqueda_ui()
        self.init_lista_ui()
        
        self.switch_to_factura()

    def create_btn(self, txt, cmd):
        btn = ctk.CTkButton(self.sidebar, text=txt, height=45, fg_color="transparent", anchor="w", command=cmd)
        btn.pack(pady=5, padx=15, fill="x")
        return btn

    def init_facturacion_ui(self):
        self.view_facturacion.grid_columnconfigure(0, weight=2)
        self.view_facturacion.grid_columnconfigure(1, weight=3)
        self.view_facturacion.grid_rowconfigure(0, weight=1)

        f_left = ctk.CTkFrame(self.view_facturacion)
        f_left.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(f_left, text="DATOS DE COBRO", font=("Segoe UI", 20, "bold")).pack(pady=20)
        
        self.ent_dir = self.create_in(f_left, "Dirección:")
        self.ent_dir.bind("<FocusOut>", self.on_leave_dir)
        self.lbl_status = ctk.CTkLabel(f_left, text="...", font=("Segoe UI", 11))
        self.lbl_status.pack()

        self.ent_est = self.create_in(f_left, "Estrato (1-6):")
        self.ent_con = self.create_in(f_left, "Consumo m3:")
        self.ent_tar = self.create_in(f_left, "Tarifa Base $:")

        ctk.CTkButton(f_left, text="GENERAR FACTURA", height=50, command=self.logic_generar).pack(pady=20, padx=30, fill="x")

        f_right = ctk.CTkFrame(self.view_facturacion, fg_color="#e1e4e8")
        f_right.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.txt_factura = ctk.CTkTextbox(f_right, fg_color="white", text_color="black", font=("Courier New", 14))
        self.txt_factura.pack(fill="both", expand=True, padx=20, pady=20)

    def create_in(self, p, lbl):
        ctk.CTkLabel(p, text=lbl).pack(anchor="w", padx=35)
        e = ctk.CTkEntry(p, height=35)
        e.pack(pady=(0, 10), padx=30, fill="x")
        return e

    def init_busqueda_ui(self):
        ctk.CTkLabel(self.view_busqueda, text="BUSCAR HISTORIAL", font=("Segoe UI", 24, "bold")).pack(pady=20)
        self.ent_s = ctk.CTkEntry(self.view_busqueda, placeholder_text="Dirección...", width=400)
        self.ent_s.pack(pady=10)
        ctk.CTkButton(self.view_busqueda, text="BUSCAR", command=self.logic_buscar_historial).pack(pady=5)
        self.txt_h = ctk.CTkTextbox(self.view_busqueda, height=400)
        self.txt_h.pack(fill="both", padx=40, pady=20)

    def init_lista_ui(self):
        ctk.CTkLabel(self.view_lista_total, text="TODOS LOS PREDIOS", font=("Segoe UI", 24, "bold")).pack(pady=20)
        self.txt_l = ctk.CTkTextbox(self.view_lista_total, fg_color="#2b2b2b")
        self.txt_l.pack(fill="both", expand=True, padx=40, pady=20)

    def switch_to_factura(self): self.hide(); self.view_facturacion.grid(row=0, column=1, sticky="nsew")
    def switch_to_buscar(self): self.hide(); self.view_busqueda.grid(row=0, column=1, sticky="nsew")
    def switch_to_lista(self): self.hide(); self.view_lista_total.grid(row=0, column=1, sticky="nsew"); self.cargar_l()
    def hide(self): 
        for v in [self.view_facturacion, self.view_busqueda, self.view_lista_total]: v.grid_forget()

    def on_leave_dir(self, e):
        d = self.ent_dir.get().strip().lower()
        est, _ = buscar_datos_predio(d)
        if est:
            self.ent_est.delete(0, 'end'); self.ent_est.insert(0, str(est))
            self.lbl_status.configure(text="✅ REGISTRADO", text_color="green")
        else: self.lbl_status.configure(text="🆕 NUEVO", text_color="blue")

    def logic_generar(self):
        try:
            d = self.ent_dir.get().strip()
            est = int(self.ent_est.get())
            con = float(self.ent_con.get())
            tar = float(self.ent_tar.get())
            sub = {1:0.5, 2:0.25, 3:0.1}.get(est, 0.0)
            bruto = con * tar
            neto = bruto * (1 - sub)
            
            msg = "🌱 Ahorro total" if con <= 20 else "💧 Consumo moderado" if con <= 40 else "⚠️ Consumo ALTO"
            
            f_txt = f"""
╔════════════════════════════════════╗
║         FACTURA SIGHA 2026         ║
╠════════════════════════════════════╣
  DIR: {d.upper()}
  ESTRATO: {est}
  FECHA: {datetime.now().strftime('%d/%m/%Y')}
--------------------------------------
  CONSUMO: {con} m3
  VALOR BRUTO: ${bruto:,.0f}
  SUBSIDIO:   -{int(sub*100)}%
--------------------------------------
  TOTAL NETO:  ${neto:,.0f}
--------------------------------------
  {msg}
  
  
  
  
  
  
╚════════════════════════════════════╝"""
            self.txt_factura.delete("1.0", "end"); self.txt_factura.insert("1.0", f_txt)
            guardar_registro_db({"Fecha": datetime.now().strftime("%Y-%m-%d"), "Direccion": d, "Estrato": est, "Consumo": con, "Total_Neto": neto, "Alerta_Fuga": "NO"})
        except Exception as e: self.txt_factura.insert("1.0", f"Error: {e}")

    def cargar_l(self):
        p = obtener_todos_los_predios()
        self.txt_l.delete("1.0", "end")
        header = f"{'DIRECCIÓN':<30} | {'ESTRATO':<10}\n" + "-"*45 + "\n"
        self.txt_l.insert("end", header)
        for r in p: self.txt_l.insert("end", f"{r[0].upper():<30} | {r[1]:<10}\n")

    def logic_buscar_historial(self):
        d = self.ent_s.get().strip()
        h = obtener_historial_completo(d)
        self.txt_h.delete("1.0", "end")
        for r in h: self.txt_h.insert("end", f"{r[0]} | {r[1]}m3 | ${r[2]:,.0f}\n")

    def refrescar_todo(self):
        for e in [self.ent_dir, self.ent_est, self.ent_con, self.ent_tar, self.ent_s]: e.delete(0, 'end')
        self.txt_factura.delete("1.0", "end")

if __name__ == "__main__":
    try:
        app = AppSIGHA()
        app.mainloop()
    except Exception as e:
        print(f"ERROR CRÍTICO AL INICIAR: {e}")