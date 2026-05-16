import tkinter as tk
from tkinter import messagebox
import json, os, winsound

ARCHIVO = "cajero_estado.json"
BILLETES_INIT = {50000:10, 20000:15, 10000:20, 5000:25, 1000:30}
USERS = {"1234": "0000", "5678": "1111"}  # tarjeta: pin

def cargar():
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO) as f: return json.load(f)
    return {str(k): v for k,v in BILLETES_INIT.items()}

def guardar(billetes):
    with open(ARCHIVO, "w") as f: json.dump(billetes, f)

def beep(ok=True):
    try:
        winsound.Beep(1000 if ok else 400, 300)
    except: pass

def total(billetes):
    return sum(int(k)*v for k,v in billetes.items())

def dispensar(billetes, monto):
    temp = dict(billetes)
    cambio = {}
    for denom in sorted(temp, key=int, reverse=True):
        d = int(denom)
        cant = min(monto // d, temp[denom])
        if cant:
            cambio[denom] = cant
            monto -= cant * d
            temp[denom] -= cant
    if monto != 0: return None, billetes
    return cambio, temp

class Cajero:
    def __init__(self, root):
        self.root = root
        root.title("Cajero Automático")
        root.geometry("320x420")
        root.resizable(False, False)
        root.configure(bg="#1a1a2e")
        self.billetes = cargar()
        self.user = None
        self.pantalla()

    def clear(self):
        for w in self.root.winfo_children(): w.destroy()

    def lbl(self, txt, **kw):
        kw.setdefault("bg","#1a1a2e"); kw.setdefault("fg","#e0e0e0"); kw.setdefault("font",("Courier",11))
        tk.Label(self.root, text=txt, **kw).pack(pady=4)

    def btn(self, txt, cmd, color="#16213e"):
        tk.Button(self.root, text=txt, command=cmd, bg=color, fg="white",
                  font=("Courier",10,"bold"), relief="flat", padx=10, pady=6).pack(pady=3, fill="x", padx=30)

    def entrada(self, show=""):
        e = tk.Entry(self.root, bg="#0f3460", fg="white", font=("Courier",14), show=show,
                     insertbackground="white", justify="center")
        e.pack(pady=4, ipady=6, padx=30, fill="x")
        return e

    def pantalla(self):
        self.clear()
        if total(self.billetes) == 0:
            self.lbl("⛔ FUERA DE SERVICIO", fg="#ff4444", font=("Courier",14,"bold"))
            return
        self.lbl("💳 CAJERO AUTOMÁTICO", font=("Courier",13,"bold"), fg="#e94560")
        self.lbl("Número de tarjeta:")
        self.e_tarjeta = self.entrada()
        self.lbl("PIN:")
        self.e_pin = self.entrada(show="*")
        self.btn("Ingresar", self.login, "#e94560")

    def login(self):
        t = self.e_tarjeta.get().strip()
        p = self.e_pin.get().strip()
        if USERS.get(t) == p:
            beep(True); self.user = t; self.menu()
        else:
            beep(False); messagebox.showerror("Error","Tarjeta o PIN incorrecto")

    def menu(self):
        self.clear()
        self.lbl(f"👤 Bienvenido", fg="#4ecca3", font=("Courier",12,"bold"))
        self.lbl(f"Disponible en cajero: ${total(self.billetes):,}")
        self.btn("Retirar dinero", self.retirar)
        self.btn("Ver billetes disponibles", self.ver_billetes)
        self.btn("Salir", self.pantalla, "#555")

    def ver_billetes(self):
        txt = "\n".join(f"  ${int(k):,} × {v}" for k,v in sorted(self.billetes.items(), key=lambda x: -int(x[0])))
        messagebox.showinfo("Billetes en cajero", txt)

    def retirar(self):
        self.clear()
        self.lbl("💵 RETIRO", fg="#4ecca3", font=("Courier",12,"bold"))
        self.lbl("Ingrese monto ($):")
        self.e_monto = self.entrada()
        self.btn("Retirar", self.procesar_retiro, "#e94560")
        self.btn("Volver", self.menu, "#555")

    def procesar_retiro(self):
        try:
            monto = int(self.e_monto.get().replace(",","").replace(".",""))
        except:
            beep(False); messagebox.showerror("Error","Ingrese un monto válido"); return
        if monto <= 0:
            beep(False); messagebox.showerror("Error","Monto debe ser positivo"); return
        if monto > total(self.billetes):
            beep(False); messagebox.showerror("Sin fondos","Cajero sin fondos suficientes"); return
        cambio, nuevo = dispensar(self.billetes, monto)
        if cambio is None:
            beep(False); messagebox.showerror("Error","No se puede dar ese monto exacto con los billetes disponibles"); return
        self.billetes = nuevo
        guardar(self.billetes)
        beep(True)
        detalle = "\n".join(f"  ${int(k):,} × {v}" for k,v in sorted(cambio.items(), key=lambda x:-int(x[0])))
        messagebox.showinfo("✅ Retiro exitoso", f"Reciba:\n{detalle}\n\nTotal: ${monto:,}")
        if total(self.billetes) == 0:
            messagebox.showwarning("Sin fondos","El cajero quedó sin billetes.")
        self.menu()

root = tk.Tk()
Cajero(root)
root.mainloop()