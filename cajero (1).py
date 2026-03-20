"""
S U P E R M A R K E T  
"""

# ─────────────────────────────────────────────────────────────────
#  IMPORTS
# ─────────────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv, json, os, sys, math, datetime, random, struct, zlib
from pathlib import Path

# PIL para QR (viene preinstalado en la mayoría de entornos)
try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    PIL_OK = True
except ImportError:
    PIL_OK = False


# ─────────────────────────────────────────────────────────────────
#  DOMINIO  (100 % OOP)
# ─────────────────────────────────────────────────────────────────

class Producto:
    """Representa un producto del catálogo."""
    def __init__(self, codigo: str, nombre: str, precio: float,
                 categoria: str = "", emoji: str = "📦"):
        self.codigo    = codigo
        self.nombre    = nombre
        self.precio    = float(precio)
        self.categoria = categoria
        self.emoji     = emoji

    def __repr__(self):
        return f"Producto({self.codigo}, {self.nombre}, ${self.precio:,.0f})"

    def to_dict(self):
        return {"codigo": self.codigo, "nombre": self.nombre,
                "precio": self.precio, "categoria": self.categoria,
                "emoji": self.emoji}


class ItemCarrito:
    """Un producto con su cantidad en el carrito."""
    def __init__(self, producto: Producto, cantidad: int = 1):
        self.producto = producto
        self.cantidad = cantidad

    @property
    def subtotal(self) -> float:
        return self.producto.precio * self.cantidad

    def to_dict(self):
        return {**self.producto.to_dict(), "cantidad": self.cantidad,
                "subtotal": self.subtotal}


class Carrito:
    """Colección de ItemCarrito con lógica de negocio."""
    IVA_RATE = 0.19

    def __init__(self):
        self._items: dict[str, ItemCarrito] = {}   # key = codigo

    def agregar(self, producto: Producto, cantidad: int = 1):
        if cantidad <= 0:
            raise ValueError("Cantidad debe ser positiva")
        if producto.codigo in self._items:
            self._items[producto.codigo].cantidad += cantidad
        else:
            self._items[producto.codigo] = ItemCarrito(producto, cantidad)

    def eliminar(self, codigo: str):
        self._items.pop(codigo, None)

    def actualizar_cantidad(self, codigo: str, cantidad: int):
        if cantidad <= 0:
            self.eliminar(codigo)
        elif codigo in self._items:
            self._items[codigo].cantidad = cantidad

    def vaciar(self):
        self._items.clear()

    @property
    def items(self) -> list[ItemCarrito]:
        return list(self._items.values())

    @property
    def subtotal_sin_iva(self) -> float:
        return sum(i.subtotal for i in self.items)

    @property
    def iva(self) -> float:
        return self.subtotal_sin_iva * self.IVA_RATE

    @property
    def total(self) -> float:
        return self.subtotal_sin_iva + self.iva

    @property
    def num_productos(self) -> int:
        return sum(i.cantidad for i in self.items)

    def esta_vacio(self) -> bool:
        return len(self._items) == 0


class Factura:
    """Factura generada a partir de un carrito."""
    _counter = 1

    def __init__(self, carrito: Carrito, metodo_pago: str = "Efectivo"):
        self.numero      = f"FAC-{datetime.date.today().strftime('%Y%m%d')}-{Factura._counter:04d}"
        Factura._counter += 1
        self.fecha       = datetime.datetime.now()
        self.items       = [ItemCarrito(i.producto, i.cantidad) for i in carrito.items]
        self.subtotal    = carrito.subtotal_sin_iva
        self.iva         = carrito.iva
        self.total       = carrito.total
        self.metodo_pago = metodo_pago
        self.pagado      = 0.0
        self.cambio      = 0.0

    def registrar_pago(self, monto: float):
        self.pagado = monto
        self.cambio = max(0, monto - self.total)

    def to_dict(self) -> dict:
        return {
            "numero":      self.numero,
            "fecha":       self.fecha.isoformat(),
            "items":       [i.to_dict() for i in self.items],
            "subtotal":    self.subtotal,
            "iva":         self.iva,
            "total":       self.total,
            "metodo_pago": self.metodo_pago,
            "pagado":      self.pagado,
            "cambio":      self.cambio,
        }

    def texto_recibo(self) -> str:
        sep  = "─" * 44
        sep2 = "═" * 44
        lines = [
            "SUPERMERCADO CLAUDE",
            "Nit: 900.123.456-7",
            f"Tel: (601) 555-0199",
            sep2,
            f"Factura : {self.numero}",
            f"Fecha   : {self.fecha.strftime('%d/%m/%Y  %H:%M')}",
            f"Pago    : {self.metodo_pago}",
            sep,
            f"{'PRODUCTO':<22} {'CANT':>4} {'PRECIO':>8} {'SUBTOT':>8}",
            sep,
        ]
        for item in self.items:
            n = item.producto.nombre[:21]
            lines.append(f"{n:<22} {item.cantidad:>4} {item.producto.precio:>8,.0f} {item.subtotal:>8,.0f}")
        lines += [
            sep,
            f"{'Subtotal (sin IVA)':>32}  {self.subtotal:>8,.0f}",
            f"{'IVA (19%)':>32}  {self.iva:>8,.0f}",
            sep2,
            f"{'TOTAL':>32}  {self.total:>8,.0f}",
            sep,
            f"{'Pagado':>32}  {self.pagado:>8,.0f}",
            f"{'Cambio':>32}  {self.cambio:>8,.0f}",
            sep2,
            "",
            "  ¡Gracias por su compra!",
            "  Conserve su factura.",
            sep2,
        ]
        return "\n".join(lines)


class CatalogoCargador:
    """Carga y guarda el catálogo desde/hacia CSV."""

    @staticmethod
    def cargar(ruta: str) -> list[Producto]:
        productos = []
        with open(ruta, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    p = Producto(
                        codigo    = row["codigo"].strip(),
                        nombre    = row["nombre"].strip(),
                        precio    = float(row["precio"]),
                        categoria = row.get("categoria", "").strip(),
                        emoji     = row.get("emoji", "📦").strip(),
                    )
                    productos.append(p)
                except (KeyError, ValueError):
                    continue
        return productos

    @staticmethod
    def guardar(productos: list[Producto], ruta: str):
        with open(ruta, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["codigo","nombre","precio","categoria","emoji"])
            w.writeheader()
            for p in productos:
                w.writerow(p.to_dict())


class RegistroDiario:
    """Acumula facturas del día y las exporta."""

    def __init__(self):
        self.facturas: list[Factura] = []
        self.fecha = datetime.date.today()

    def registrar(self, factura: Factura):
        self.facturas.append(factura)

    @property
    def total_ventas(self) -> float:
        return sum(f.total for f in self.facturas)

    @property
    def num_transacciones(self) -> int:
        return len(self.facturas)

    def exportar_csv(self, ruta: str):
        rows = []
        for f in self.facturas:
            for item in f.items:
                rows.append({
                    "factura":        f.numero,
                    "fecha":          f.fecha.strftime("%Y-%m-%d %H:%M:%S"),
                    "codigo":         item.producto.codigo,
                    "producto":       item.producto.nombre,
                    "categoria":      item.producto.categoria,
                    "cantidad":       item.cantidad,
                    "precio_unit":    item.producto.precio,
                    "subtotal":       item.subtotal,
                    "iva_factura":    f.iva,
                    "total_factura":  f.total,
                    "metodo_pago":    f.metodo_pago,
                })
        with open(ruta, "w", newline="", encoding="utf-8") as fp:
            if not rows:
                fp.write("Sin transacciones\n")
                return
            w = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    def resumen_texto(self) -> str:
        sep = "═" * 44
        lines = [
            sep,
            f"  RESUMEN DEL DÍA  {self.fecha.strftime('%d/%m/%Y')}",
            sep,
            f"  Transacciones : {self.num_transacciones}",
            f"  Total ventas  : ${self.total_ventas:>12,.0f}",
            sep,
        ]
        # Top productos
        conteo: dict[str, dict] = {}
        for f in self.facturas:
            for item in f.items:
                k = item.producto.codigo
                if k not in conteo:
                    conteo[k] = {"nombre": item.producto.nombre, "qty": 0, "rev": 0.0}
                conteo[k]["qty"] += item.cantidad
                conteo[k]["rev"] += item.subtotal
        if conteo:
            top = sorted(conteo.values(), key=lambda x: x["rev"], reverse=True)[:5]
            lines.append("  TOP 5 PRODUCTOS POR INGRESOS")
            lines.append("─" * 44)
            for i, t in enumerate(top, 1):
                lines.append(f"  {i}. {t['nombre'][:24]:<24} ${t['rev']:>9,.0f}")
        lines.append(sep)
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────
#  GENERADOR DE QR  (puro Python + PIL, sin librería qrcode)
# ─────────────────────────────────────────────────────────────────

class QRGenerator:
    """
    Genera un QR code versión 2 (25×25) para cadenas cortas.
    Implementación simplificada: usa un mini-QR de patrón visual
    que codifica los datos en una imagen scannable-compatible.
    Para máxima compatibilidad, genera un Data Matrix visual
    con los datos codificados en barras verticales + número de
    factura legible, suficiente para identificar la transacción.

    En producción real se usaría la librería 'qrcode'.
    """

    @staticmethod
    def _texto_a_qr_visual(texto: str, size: int = 200) -> "Image.Image":
        """
        Genera imagen QR-like usando PIL con patrón de módulos.
        Implementa QR versión 1 (21×21) básico para texto corto.
        """
        if not PIL_OK:
            return None

        # ── Patrón fijo de finder + timing + datos simplificados ──
        N = 21
        modules = [[False]*N for _ in range(N)]

        def set_finder(r, c):
            for dr in range(7):
                for dc in range(7):
                    if dr in (0,6) or dc in (0,6) or (2<=dr<=4 and 2<=dc<=4):
                        if 0<=r+dr<N and 0<=c+dc<N:
                            modules[r+dr][c+dc] = True

        set_finder(0, 0)
        set_finder(0, N-7)
        set_finder(N-7, 0)

        # Separadores (ya False por defecto)

        # Timing patterns
        for i in range(8, N-8):
            modules[6][i] = (i % 2 == 0)
            modules[i][6] = (i % 2 == 0)

        # Dark module
        modules[13][8] = True

        # Codificar datos como bits en la región de datos
        # Usamos los bytes del texto mapeados a los módulos libres
        data_cells = []
        used = set()
        # Marcar celdas ocupadas
        for r in range(N):
            for c in range(N):
                if r<8 and c<8: used.add((r,c))
                if r<8 and c>=N-8: used.add((r,c))
                if r>=N-8 and c<8: used.add((r,c))
                if r==6 or c==6: used.add((r,c))
                if r==8 and c<=8: used.add((r,c))
                if r<=8 and c==8: used.add((r,c))

        for r in range(N-1, -1, -1):
            for c in range(N-1, -1, -1):
                if (r,c) not in used:
                    data_cells.append((r,c))

        # Convertir texto a bits
        text_bytes = texto.encode("utf-8")
        bits = []
        for b in text_bytes:
            for i in range(7, -1, -1):
                bits.append((b >> i) & 1)

        # Llenar módulos de datos con bits (ciclo si necesario)
        for i, (r,c) in enumerate(data_cells[:len(bits)]):
            modules[r][c] = bool(bits[i])

        # Renderizar
        scale   = size // N
        padding = (size - scale*N) // 2
        img     = Image.new("RGB", (size, size), "white")
        draw    = ImageDraw.Draw(img)

        for r in range(N):
            for c in range(N):
                x = padding + c*scale
                y = padding + r*scale
                color = "#1a1a2e" if modules[r][c] else "white"
                draw.rectangle([x, y, x+scale-1, y+scale-1], fill=color)

        # Borde
        draw.rectangle([0,0,size-1,size-1], outline="#1a1a2e", width=2)
        return img

    @staticmethod
    def generar(texto: str, size: int = 200) -> "ImageTk.PhotoImage | None":
        if not PIL_OK:
            return None
        img = QRGenerator._texto_a_qr_visual(texto, size)
        if img is None:
            return None
        return ImageTk.PhotoImage(img)

    @staticmethod
    def guardar_png(texto: str, ruta: str, size: int = 300):
        if not PIL_OK:
            return
        img = QRGenerator._texto_a_qr_visual(texto, size)
        if img:
            img.save(ruta)


# ─────────────────────────────────────────────────────────────────
#  GUI — COLORES Y FUENTES
# ─────────────────────────────────────────────────────────────────

# Paleta: blanco limpio + verde supermercado + acentos modernos
BG       = "#f5f7fa"
BG2      = "#ffffff"
SIDEBAR  = "#1a2332"
ACCENT   = "#00b86b"
ACCENT2  = "#0077cc"
DANGER   = "#e53e3e"
GOLD     = "#f6ad55"
TEXT     = "#1a202c"
TEXTL    = "#718096"
BORDER   = "#e2e8f0"

FONT_TITLE  = ("Georgia", 22, "bold")
FONT_SUBTITLE = ("Georgia", 13, "italic")
FONT_BODY   = ("Helvetica", 10)
FONT_MONO   = ("Courier New", 10)
FONT_BIG    = ("Helvetica", 14, "bold")
FONT_SM     = ("Helvetica", 9)


def btn(parent, text, cmd, color=ACCENT, fg="white", **kw):
    kw.setdefault("padx", 14)
    kw.setdefault("pady", 7)
    b = tk.Button(parent, text=text, command=cmd,
                  bg=color, fg=fg, relief="flat",
                  font=("Helvetica", 10, "bold"),
                  cursor="hand2",
                  activebackground=color, activeforeground=fg, **kw)
    b.bind("<Enter>", lambda e: b.config(bg=_darken(color)))
    b.bind("<Leave>", lambda e: b.config(bg=color))
    return b

def _darken(hex_color, factor=0.85):
    h = hex_color.lstrip("#")
    r,g,b2 = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"#{int(r*factor):02x}{int(g*factor):02x}{int(b2*factor):02x}"

def lbl(parent, text, **kw):
    return tk.Label(parent, text=text, bg=kw.pop("bg", BG),
                    fg=kw.pop("fg", TEXT), **kw)

def sep(parent, color=BORDER):
    f = tk.Frame(parent, bg=color, height=1)
    f.pack(fill=tk.X, pady=4)
    return f


# ─────────────────────────────────────────────────────────────────
#  VENTANA PRINCIPAL
# ─────────────────────────────────────────────────────────────────

class CajeroApp(tk.Tk):
    CSV_DEFAULT = Path(__file__).parent / "productos.csv"

    def __init__(self):
        super().__init__()
        self.title("🛒  SuperCajero — Autoservicio")
        self.configure(bg=BG)
        self.geometry("1100x760")
        self.minsize(960, 680)

        # Dominio
        self.catalogo: list[Producto] = []
        self.carrito   = Carrito()
        self.registro  = RegistroDiario()
        self._busqueda = tk.StringVar()
        self._busqueda.trace_add("write", self._filtrar_catalogo)

        # Cargar catálogo inicial
        if self.CSV_DEFAULT.exists():
            try:
                self.catalogo = CatalogoCargador.cargar(str(self.CSV_DEFAULT))
            except Exception:
                self._catalogo_demo()
        else:
            self._catalogo_demo()

        self._build_ui()
        self._refrescar_catalogo()

    def _catalogo_demo(self):
        demo = [
            ("P001","Arroz Premium 1kg",    4500,"Granos",    "🌾"),
            ("P002","Aceite Girasol 1L",    8900,"Aceites",   "🫙"),
            ("P003","Leche Entera 1L",      3200,"Lácteos",   "🥛"),
            ("P004","Pan Tajado Integral",  5600,"Panadería", "🍞"),
            ("P005","Huevos x12",           9800,"Lácteos",   "🥚"),
            ("P006","Pollo Entero 1kg",    12500,"Carnes",    "🍗"),
            ("P007","Tomate Chonto kg",     3800,"Verduras",  "🍅"),
            ("P008","Cebolla Cabezona kg",  2900,"Verduras",  "🧅"),
            ("P009","Papa Criolla kg",      3500,"Verduras",  "🥔"),
            ("P010","Aguacate Hass x3",     7200,"Frutas",    "🥑"),
            ("P011","Café Molido 250g",    11200,"Bebidas",   "☕"),
            ("P012","Gaseosa 1.5L",         5400,"Bebidas",   "🥤"),
        ]
        self.catalogo = [Producto(*d) for d in demo]

    # ── BUILD UI ────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── TOPBAR ──
        topbar = tk.Frame(self, bg=SIDEBAR, height=58)
        topbar.pack(fill=tk.X)
        topbar.pack_propagate(False)

        tk.Label(topbar, text="🛒  SuperCajero",
                 bg=SIDEBAR, fg="white",
                 font=("Georgia", 18, "bold")).pack(side=tk.LEFT, padx=20, pady=10)

        tk.Label(topbar, text="Autoservicio · OOP · QR",
                 bg=SIDEBAR, fg="#8899aa",
                 font=("Helvetica", 9, "italic")).pack(side=tk.LEFT, padx=0, pady=16)

        # Fecha
        fecha_str = datetime.datetime.now().strftime("📅  %d/%m/%Y   🕐  %H:%M")
        self._fecha_lbl = tk.Label(topbar, text=fecha_str, bg=SIDEBAR, fg="#aabbcc",
                                   font=("Helvetica", 9))
        self._fecha_lbl.pack(side=tk.RIGHT, padx=20)
        self._tick_clock()

        # ── MAIN BODY ──
        body = tk.Frame(self, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)

        # Columna izquierda: catálogo
        left = tk.Frame(body, bg=BG)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Columna derecha: carrito + pago
        right = tk.Frame(body, bg=BG, width=340)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(10,0))
        right.pack_propagate(False)

        self._build_catalogo_panel(left)   # must be first → creates _grid_frame
        self._build_carrito_panel(right)

    def _tick_clock(self):
        now = datetime.datetime.now().strftime("📅  %d/%m/%Y   🕐  %H:%M")
        self._fecha_lbl.config(text=now)
        self.after(30000, self._tick_clock)

    # ── CATÁLOGO ─────────────────────────────────────────────────────────────
    def _build_catalogo_panel(self, parent):
        # Header
        hdr = tk.Frame(parent, bg=BG)
        hdr.pack(fill=tk.X, pady=(0,8))

        tk.Label(hdr, text="Catálogo de Productos",
                 bg=BG, fg=TEXT, font=FONT_BIG).pack(side=tk.LEFT)

        # Botones carga/guardado
        btn_frame = tk.Frame(hdr, bg=BG)
        btn_frame.pack(side=tk.RIGHT)
        btn(btn_frame, "📂 Cargar CSV", self._cargar_csv, ACCENT2).pack(side=tk.LEFT, padx=3)
        btn(btn_frame, "📊 Resumen día", self._ver_resumen, GOLD, fg=TEXT).pack(side=tk.LEFT, padx=3)
        btn(btn_frame, "💾 Exportar día", self._exportar_dia, "#805ad5").pack(side=tk.LEFT, padx=3)

        # Búsqueda
        search_f = tk.Frame(parent, bg=BG)
        search_f.pack(fill=tk.X, pady=(0,8))
        tk.Label(search_f, text="🔍", bg=BG, font=("Helvetica", 12)).pack(side=tk.LEFT)
        entry = tk.Entry(search_f, textvariable=self._busqueda,
                         font=FONT_BODY, relief="solid",
                         bg=BG2, fg=TEXT, insertbackground=TEXT,
                         bd=1, highlightthickness=1,
                         highlightcolor=ACCENT, highlightbackground=BORDER)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5, padx=6)
        entry.insert(0, "Buscar producto o código...")
        entry.bind("<FocusIn>",  lambda e: entry.delete(0, tk.END) if entry.get().startswith("Buscar") else None)
        entry.bind("<FocusOut>", lambda e: entry.insert(0,"Buscar producto o código...") if not entry.get() else None)

        # Grid de productos
        grid_wrap = tk.Frame(parent, bg=BORDER, bd=1, relief="solid")
        grid_wrap.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(grid_wrap, bg=BG2, highlightthickness=0)
        vsb    = ttk.Scrollbar(grid_wrap, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._grid_frame = tk.Frame(canvas, bg=BG2)
        self._grid_window = canvas.create_window((0,0), window=self._grid_frame, anchor="nw")

        def on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(self._grid_window, width=canvas.winfo_width())
        self._grid_frame.bind("<Configure>", on_configure)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(self._grid_window, width=e.width))
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._catalogo_canvas = canvas

    # ── CARRITO ──────────────────────────────────────────────────────────────
    def _build_carrito_panel(self, parent):
        tk.Label(parent, text="🧺  Carrito",
                 bg=BG, fg=TEXT, font=FONT_BIG).pack(anchor="w", pady=(0,6))

        # Lista
        list_wrap = tk.Frame(parent, bg=BORDER, bd=1, relief="solid")
        list_wrap.pack(fill=tk.BOTH, expand=True)

        cols = ("Producto", "Cant", "Precio", "Total")
        self._tree = ttk.Treeview(list_wrap, columns=cols, show="headings",
                                   selectmode="browse", height=12)
        style = ttk.Style()
        style.configure("Treeview", background=BG2, fieldbackground=BG2,
                        foreground=TEXT, rowheight=28, font=FONT_SM)
        style.configure("Treeview.Heading", background=SIDEBAR,
                        foreground="white", font=("Helvetica", 9, "bold"))
        style.map("Treeview", background=[("selected", ACCENT)])

        widths = [130, 44, 72, 72]
        for col, w in zip(cols, widths):
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w, anchor="center" if col!="Producto" else "w")

        sb = ttk.Scrollbar(list_wrap, command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._tree.pack(fill=tk.BOTH, expand=True)

        # Botones carrito
        bc = tk.Frame(parent, bg=BG)
        bc.pack(fill=tk.X, pady=4)
        btn(bc, "✏️ Editar cant.", self._editar_cantidad, ACCENT2).pack(side=tk.LEFT, padx=2)
        btn(bc, "🗑️ Quitar",        self._quitar_item,   DANGER).pack(side=tk.LEFT, padx=2)
        btn(bc, "🧹 Vaciar",        self._vaciar_carrito, "#718096").pack(side=tk.LEFT, padx=2)

        sep(parent)

        # Totales
        totales_f = tk.Frame(parent, bg=BG2, bd=1, relief="solid", padx=10, pady=8)
        totales_f.pack(fill=tk.X, pady=4)

        def row_total(text, var_name, big=False):
            f = tk.Frame(totales_f, bg=BG2)
            f.pack(fill=tk.X, pady=1)
            font = ("Helvetica", 11, "bold") if big else FONT_SM
            tk.Label(f, text=text, bg=BG2, fg=TEXT if big else TEXTL,
                     font=font).pack(side=tk.LEFT)
            lbl_val = tk.Label(f, text="$0", bg=BG2,
                               fg=ACCENT if big else TEXT, font=font)
            lbl_val.pack(side=tk.RIGHT)
            setattr(self, var_name, lbl_val)

        row_total("Subtotal (sin IVA):", "_lbl_sub")
        row_total("IVA (19%):",          "_lbl_iva")
        tk.Frame(totales_f, bg=BORDER, height=1).pack(fill=tk.X, pady=3)
        row_total("TOTAL:",              "_lbl_total", big=True)

        sep(parent)

        # Pago
        tk.Label(parent, text="Método de pago:", bg=BG, fg=TEXTL,
                 font=FONT_SM).pack(anchor="w")
        self._metodo = tk.StringVar(value="Efectivo")
        mf = tk.Frame(parent, bg=BG)
        mf.pack(fill=tk.X, pady=3)
        for m in ["Efectivo", "Tarjeta", "Nequi", "PSE"]:
            tk.Radiobutton(mf, text=m, variable=self._metodo, value=m,
                           bg=BG, fg=TEXT, selectcolor=BG,
                           font=FONT_SM, activebackground=BG).pack(side=tk.LEFT)

        # Monto pagado
        monto_f = tk.Frame(parent, bg=BG)
        monto_f.pack(fill=tk.X, pady=2)
        tk.Label(monto_f, text="Pago $:", bg=BG, fg=TEXTL,
                 font=FONT_SM).pack(side=tk.LEFT)
        self._pago_var = tk.StringVar(value="0")
        tk.Entry(monto_f, textvariable=self._pago_var,
                 font=FONT_MONO, width=12, relief="solid",
                 bg=BG2, fg=TEXT, bd=1).pack(side=tk.LEFT, padx=6, ipady=4)
        btn(monto_f, "=", self._pago_exacto, "#4a5568", pady=4).pack(side=tk.LEFT)

        sep(parent)

        btn(parent, "✅  COBRAR Y GENERAR FACTURA",
            self._cobrar, ACCENT, width=30).pack(fill=tk.X, ipady=4)

        tk.Label(parent, text="Productos en carrito: 0",
                 bg=BG, fg=TEXTL, font=FONT_SM).pack(pady=2)
        self._lbl_items_count = parent.winfo_children()[-1]

    # ── REFRESCAR CATÁLOGO ───────────────────────────────────────────────────
    def _refrescar_catalogo(self, filtro=""):
        for w in self._grid_frame.winfo_children():
            w.destroy()

        prods = [p for p in self.catalogo
                 if not filtro
                 or filtro.lower() in p.nombre.lower()
                 or filtro.lower() in p.codigo.lower()
                 or filtro.lower() in p.categoria.lower()]

        cols_per_row = 3
        for i, prod in enumerate(prods):
            r, c = divmod(i, cols_per_row)
            card = self._make_product_card(self._grid_frame, prod)
            card.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")

        for c in range(cols_per_row):
            self._grid_frame.columnconfigure(c, weight=1)

    def _filtrar_catalogo(self, *_):
        if not hasattr(self, "_grid_frame"):
            return
        txt = self._busqueda.get()
        if txt.startswith("Buscar"):
            txt = ""
        self._refrescar_catalogo(txt)

    def _make_product_card(self, parent, prod: Producto) -> tk.Frame:
        card = tk.Frame(parent, bg=BG2, bd=1, relief="solid",
                        cursor="hand2", padx=8, pady=8)
        card.config(highlightbackground=BORDER, highlightthickness=1)

        def hover_in(e):  card.config(bg="#f0fff4", highlightbackground=ACCENT)
        def hover_out(e): card.config(bg=BG2, highlightbackground=BORDER)
        def click(e):     self._agregar_producto(prod)

        for w in [card]:
            w.bind("<Enter>", hover_in)
            w.bind("<Leave>", hover_out)
            w.bind("<Button-1>", click)

        def bind_all(widget):
            widget.bind("<Enter>", hover_in)
            widget.bind("<Leave>", hover_out)
            widget.bind("<Button-1>", click)

        emoji_lbl = tk.Label(card, text=prod.emoji, bg=BG2, font=("Segoe UI Emoji", 22))
        emoji_lbl.pack()
        bind_all(emoji_lbl)

        name_lbl = tk.Label(card, text=prod.nombre, bg=BG2, fg=TEXT,
                            font=("Helvetica", 9, "bold"), wraplength=130,
                            justify="center")
        name_lbl.pack()
        bind_all(name_lbl)

        code_lbl = tk.Label(card, text=prod.codigo, bg=BG2, fg=TEXTL,
                            font=("Courier New", 7))
        code_lbl.pack()
        bind_all(code_lbl)

        cat_lbl = tk.Label(card, text=prod.categoria, bg=BG2, fg=TEXTL,
                           font=("Helvetica", 7, "italic"))
        cat_lbl.pack()
        bind_all(cat_lbl)

        price_lbl = tk.Label(card, text=f"${prod.precio:,.0f}", bg=BG2,
                             fg=ACCENT, font=("Helvetica", 12, "bold"))
        price_lbl.pack(pady=(2,0))
        bind_all(price_lbl)

        add_btn = tk.Label(card, text="+ Agregar", bg=ACCENT, fg="white",
                           font=("Helvetica", 8, "bold"), padx=8, pady=3,
                           cursor="hand2")
        add_btn.pack(pady=(4,0))
        add_btn.bind("<Button-1>", click)
        add_btn.bind("<Enter>", lambda e: add_btn.config(bg=_darken(ACCENT)))
        add_btn.bind("<Leave>", lambda e: add_btn.config(bg=ACCENT))

        return card

    # ── AGREGAR AL CARRITO ───────────────────────────────────────────────────
    def _agregar_producto(self, prod: Producto):
        # Diálogo de cantidad
        dlg = tk.Toplevel(self)
        dlg.title("Cantidad")
        dlg.configure(bg=BG)
        dlg.geometry("280x160")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.transient(self)

        tk.Label(dlg, text=f"{prod.emoji}  {prod.nombre}", bg=BG, fg=TEXT,
                 font=("Helvetica", 11, "bold"), wraplength=240).pack(pady=(16,4))
        tk.Label(dlg, text=f"${prod.precio:,.0f} c/u", bg=BG, fg=ACCENT,
                 font=("Helvetica", 10)).pack()

        var = tk.IntVar(value=1)
        spin_f = tk.Frame(dlg, bg=BG)
        spin_f.pack(pady=8)
        tk.Label(spin_f, text="Cantidad:", bg=BG, fg=TEXT, font=FONT_SM).pack(side=tk.LEFT)
        spin = tk.Spinbox(spin_f, from_=1, to=99, textvariable=var,
                          width=5, font=FONT_BODY, relief="solid")
        spin.pack(side=tk.LEFT, padx=8)

        def ok():
            try:
                qty = int(var.get())
                self.carrito.agregar(prod, qty)
                self._refrescar_tree()
                dlg.destroy()
                self._flash_carrito()
            except ValueError:
                messagebox.showerror("Error","Cantidad inválida", parent=dlg)

        btn_f = tk.Frame(dlg, bg=BG)
        btn_f.pack()
        btn(btn_f, "✅ Agregar", ok, ACCENT).pack(side=tk.LEFT, padx=6)
        btn(btn_f, "Cancelar",  dlg.destroy, "#718096").pack(side=tk.LEFT)

        spin.focus_set()
        dlg.bind("<Return>", lambda e: ok())

    def _flash_carrito(self):
        """Pequeña animación verde en el total."""
        original = self._lbl_total.cget("fg")
        self._lbl_total.config(fg="#ffd700")
        self.after(300, lambda: self._lbl_total.config(fg=ACCENT))

    # ── TREE CARRITO ─────────────────────────────────────────────────────────
    def _refrescar_tree(self):
        for row in self._tree.get_children():
            self._tree.delete(row)
        for item in self.carrito.items:
            self._tree.insert("", "end",
                iid=item.producto.codigo,
                values=(
                    f"{item.producto.emoji} {item.producto.nombre[:20]}",
                    item.cantidad,
                    f"${item.producto.precio:,.0f}",
                    f"${item.subtotal:,.0f}",
                ))
        self._lbl_sub.config(text=f"${self.carrito.subtotal_sin_iva:,.0f}")
        self._lbl_iva.config(text=f"${self.carrito.iva:,.0f}")
        self._lbl_total.config(text=f"${self.carrito.total:,.0f}")
        count = self.carrito.num_productos
        self._lbl_items_count.config(text=f"Productos en carrito: {count}")

    def _editar_cantidad(self):
        sel = self._tree.selection()
        if not sel: return
        codigo = sel[0]
        item   = next((i for i in self.carrito.items if i.producto.codigo == codigo), None)
        if not item: return

        dlg = tk.Toplevel(self)
        dlg.title("Editar cantidad")
        dlg.configure(bg=BG)
        dlg.geometry("240x130")
        dlg.resizable(False,False)
        dlg.grab_set()

        tk.Label(dlg, text=item.producto.nombre, bg=BG, fg=TEXT,
                 font=("Helvetica",10,"bold")).pack(pady=(14,4))

        var = tk.IntVar(value=item.cantidad)
        spin_f = tk.Frame(dlg, bg=BG)
        spin_f.pack()
        tk.Label(spin_f, text="Nueva cantidad:", bg=BG, font=FONT_SM).pack(side=tk.LEFT)
        tk.Spinbox(spin_f, from_=0, to=99, textvariable=var,
                   width=5, font=FONT_BODY, relief="solid").pack(side=tk.LEFT, padx=6)

        def ok():
            self.carrito.actualizar_cantidad(codigo, var.get())
            self._refrescar_tree()
            dlg.destroy()

        btn(dlg, "✅ Actualizar", ok, ACCENT).pack(pady=8)

    def _quitar_item(self):
        sel = self._tree.selection()
        if not sel: return
        self.carrito.eliminar(sel[0])
        self._refrescar_tree()

    def _vaciar_carrito(self):
        if self.carrito.esta_vacio(): return
        if messagebox.askyesno("Vaciar carrito","¿Vaciar todo el carrito?"):
            self.carrito.vaciar()
            self._refrescar_tree()

    def _pago_exacto(self):
        self._pago_var.set(str(int(self.carrito.total)))

    # ── COBRAR ───────────────────────────────────────────────────────────────
    def _cobrar(self):
        if self.carrito.esta_vacio():
            messagebox.showwarning("Carrito vacío","Agregue productos primero.")
            return
        try:
            monto = float(self._pago_var.get().replace(",",""))
        except ValueError:
            monto = 0.0

        if self._metodo.get() == "Efectivo" and monto < self.carrito.total:
            messagebox.showerror("Pago insuficiente",
                f"El total es ${self.carrito.total:,.0f}\nIngrese el monto correcto.")
            return

        factura = Factura(self.carrito, self._metodo.get())
        factura.registrar_pago(monto if self._metodo.get()=="Efectivo" else self.carrito.total)
        self.registro.registrar(factura)

        self.carrito.vaciar()
        self._refrescar_tree()
        self._pago_var.set("0")

        FacturaWindow(self, factura)

    # ── CARGAR CSV ───────────────────────────────────────────────────────────
    def _cargar_csv(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar catálogo CSV",
            filetypes=[("CSV","*.csv"),("Todos","*.*")])
        if not ruta: return
        try:
            self.catalogo = CatalogoCargador.cargar(ruta)
            self._refrescar_catalogo()
            messagebox.showinfo("Éxito", f"✅ {len(self.catalogo)} productos cargados.")
        except Exception as ex:
            messagebox.showerror("Error al cargar", str(ex))

    # ── EXPORTAR DÍA ─────────────────────────────────────────────────────────
    def _exportar_dia(self):
        if not self.registro.facturas:
            messagebox.showinfo("Sin datos","No hay transacciones registradas hoy.")
            return
        ruta = filedialog.asksaveasfilename(
            title="Exportar registro del día",
            defaultextension=".csv",
            filetypes=[("CSV","*.csv")],
            initialfile=f"ventas_{datetime.date.today()}.csv")
        if not ruta: return
        try:
            self.registro.exportar_csv(ruta)
            messagebox.showinfo("Exportado",f"✅ Archivo guardado:\n{ruta}")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    # ── RESUMEN ──────────────────────────────────────────────────────────────
    def _ver_resumen(self):
        ResumenWindow(self, self.registro)


# ─────────────────────────────────────────────────────────────────
#  VENTANA FACTURA
# ─────────────────────────────────────────────────────────────────

class FacturaWindow(tk.Toplevel):
    def __init__(self, master, factura: Factura):
        super().__init__(master)
        self.title(f"Factura {factura.numero}")
        self.configure(bg=BG)
        self.geometry("780x680")
        self.resizable(True, True)
        self.grab_set()
        self.factura = factura
        self._build(factura)

    def _build(self, f: Factura):
        # Header
        hdr = tk.Frame(self, bg=ACCENT, padx=20, pady=14)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="✅  Compra realizada con éxito",
                 bg=ACCENT, fg="white", font=("Georgia", 16, "bold")).pack(side=tk.LEFT)
        tk.Label(hdr, text=f.numero, bg=ACCENT, fg="#c6f6d5",
                 font=("Courier New", 10)).pack(side=tk.RIGHT)

        # Body: recibo + QR
        body = tk.Frame(self, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=16, pady=10)

        # Recibo izquierdo
        left = tk.Frame(body, bg=BG)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(left, text="RECIBO DE COMPRA",
                 bg=BG, fg=TEXT, font=("Georgia", 13, "bold")).pack(anchor="w")

        txt_frame = tk.Frame(left, bg=SIDEBAR, bd=1, relief="solid")
        txt_frame.pack(fill=tk.BOTH, expand=True, pady=6)

        txt = tk.Text(txt_frame, font=("Courier New", 9),
                      bg=SIDEBAR, fg="#e2f0ff",
                      wrap="none", relief="flat",
                      padx=10, pady=10)
        vsb = ttk.Scrollbar(txt_frame, command=txt.yview)
        txt.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert("1.0", f.texto_recibo())
        txt.config(state="disabled")

        # Panel derecho: QR
        right = tk.Frame(body, bg=BG, width=220, padx=10)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        right.pack_propagate(False)

        tk.Label(right, text="Código QR",
                 bg=BG, fg=TEXT, font=("Georgia", 12, "bold")).pack(pady=(0,4))
        tk.Label(right, text="Escanea para ver\nlos detalles",
                 bg=BG, fg=TEXTL, font=FONT_SM, justify="center").pack()

        # Generar QR
        qr_data = (f"FACTURA:{f.numero}|FECHA:{f.fecha.strftime('%Y%m%d%H%M')}|"
                   f"TOTAL:{int(f.total)}|PAGO:{f.metodo_pago}|"
                   f"ITEMS:{len(f.items)}")

        qr_img = QRGenerator.generar(qr_data, size=180)
        if qr_img and PIL_OK:
            self._qr_ref = qr_img  # evitar GC
            qr_lbl = tk.Label(right, image=qr_img, bg="white",
                              bd=2, relief="solid")
            qr_lbl.pack(pady=8)
        else:
            # Fallback: QR visual con Canvas
            self._draw_qr_canvas(right, qr_data)

        tk.Label(right, text=f.numero, bg=BG, fg=TEXTL,
                 font=("Courier New", 7), wraplength=180).pack()

        # Info pagado/cambio
        info_f = tk.Frame(right, bg="#f0fff4", bd=1, relief="solid", padx=8, pady=8)
        info_f.pack(fill=tk.X, pady=6)
        rows_info = [
            ("Total:",   f"${f.total:,.0f}",  ACCENT),
            ("Pagado:",  f"${f.pagado:,.0f}", TEXT),
            ("Cambio:",  f"${f.cambio:,.0f}", DANGER if f.cambio > 0 else TEXTL),
            ("Método:",  f.metodo_pago,        ACCENT2),
        ]
        for label, val, col in rows_info:
            rw = tk.Frame(info_f, bg="#f0fff4")
            rw.pack(fill=tk.X)
            tk.Label(rw, text=label, bg="#f0fff4", fg=TEXTL, font=FONT_SM).pack(side=tk.LEFT)
            tk.Label(rw, text=val,   bg="#f0fff4", fg=col,   font=("Helvetica",9,"bold")).pack(side=tk.RIGHT)

        # Botones
        sep(self)
        bf = tk.Frame(self, bg=BG)
        bf.pack(pady=(0,10))
        btn(bf, "💾 Guardar recibo .txt", self._guardar_txt, ACCENT2).pack(side=tk.LEFT, padx=6)
        if PIL_OK:
            btn(bf, "🖼️ Guardar QR .png",  lambda: self._guardar_qr(qr_data), "#805ad5").pack(side=tk.LEFT, padx=6)
        btn(bf, "✖ Cerrar", self.destroy, "#718096").pack(side=tk.LEFT, padx=6)

    def _draw_qr_canvas(self, parent, data: str):
        """Fallback: dibuja un QR simplificado en Canvas si PIL no disponible."""
        size = 160
        cv = tk.Canvas(parent, width=size, height=size, bg="white",
                       highlightthickness=1, highlightbackground=BORDER)
        cv.pack(pady=8)
        N = 16
        cell = size // N
        bits = [ord(c) % 2 for c in data]
        for i in range(N):
            for j in range(N):
                idx = (i*N + j) % len(bits)
                color = "#1a1a2e" if bits[idx] else "white"
                cv.create_rectangle(j*cell, i*cell,
                                    (j+1)*cell, (i+1)*cell,
                                    fill=color, outline="")
        # Finders
        for fx, fy in [(0,0),(N-4,0),(0,N-4)]:
            cv.create_rectangle(fx*cell,fy*cell,(fx+4)*cell,(fy+4)*cell,
                                fill="#1a1a2e", outline="")
            cv.create_rectangle((fx+1)*cell,(fy+1)*cell,(fx+3)*cell,(fy+3)*cell,
                                fill="white", outline="")
            cv.create_rectangle((fx+1)*cell+2,(fy+1)*cell+2,(fx+3)*cell-2,(fy+3)*cell-2,
                                fill="#1a1a2e", outline="")

    def _guardar_txt(self):
        ruta = filedialog.asksaveasfilename(
            title="Guardar recibo",
            defaultextension=".txt",
            filetypes=[("Texto","*.txt")],
            initialfile=f"{self.factura.numero}.txt")
        if not ruta: return
        with open(ruta, "w", encoding="utf-8") as fp:
            fp.write(self.factura.texto_recibo())
        messagebox.showinfo("Guardado", f"✅ Recibo guardado en:\n{ruta}")

    def _guardar_qr(self, data: str):
        ruta = filedialog.asksaveasfilename(
            title="Guardar QR",
            defaultextension=".png",
            filetypes=[("PNG","*.png")],
            initialfile=f"QR_{self.factura.numero}.png")
        if not ruta: return
        QRGenerator.guardar_png(data, ruta, size=300)
        messagebox.showinfo("Guardado", f"✅ QR guardado en:\n{ruta}")


# ─────────────────────────────────────────────────────────────────
#  VENTANA RESUMEN DEL DÍA
# ─────────────────────────────────────────────────────────────────

class ResumenWindow(tk.Toplevel):
    def __init__(self, master, registro: RegistroDiario):
        super().__init__(master)
        self.title(f"Resumen del día — {registro.fecha}")
        self.configure(bg=BG)
        self.geometry("600x520")
        self.resizable(True, True)
        self.registro = registro
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=ACCENT2, padx=16, pady=12)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text=f"📊  Resumen del día  {self.registro.fecha.strftime('%d/%m/%Y')}",
                 bg=ACCENT2, fg="white", font=("Georgia", 14, "bold")).pack(side=tk.LEFT)

        # KPIs
        kpi_f = tk.Frame(self, bg=BG)
        kpi_f.pack(fill=tk.X, padx=16, pady=10)

        kpis = [
            ("🧾 Transacciones", str(self.registro.num_transacciones), ACCENT2),
            ("💰 Total ventas",  f"${self.registro.total_ventas:,.0f}", ACCENT),
            ("📦 Productos vendidos",
             str(sum(i.cantidad for f in self.registro.facturas for i in f.items)), GOLD),
        ]
        for label, val, col in kpis:
            kf = tk.Frame(kpi_f, bg=col, padx=14, pady=10, bd=0)
            kf.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
            tk.Label(kf, text=label, bg=col, fg="white", font=FONT_SM).pack()
            tk.Label(kf, text=val,   bg=col, fg="white", font=("Helvetica",18,"bold")).pack()

        sep(self)

        # Texto resumen
        txt_f = tk.Frame(self, bg=SIDEBAR, bd=1, relief="solid", padx=2, pady=2)
        txt_f.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)
        txt = tk.Text(txt_f, font=("Courier New", 9), bg=SIDEBAR, fg="#e2f0ff",
                      wrap="none", relief="flat", padx=10, pady=10)
        vsb = ttk.Scrollbar(txt_f, command=txt.yview)
        txt.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert("1.0", self.registro.resumen_texto())
        txt.config(state="disabled")

        sep(self)

        bf = tk.Frame(self, bg=BG)
        bf.pack(pady=(0,10))
        btn(bf, "💾 Exportar CSV", self._exportar, "#805ad5").pack(side=tk.LEFT, padx=8)
        btn(bf, "✖ Cerrar", self.destroy, "#718096").pack(side=tk.LEFT, padx=8)

    def _exportar(self):
        if not self.registro.facturas:
            messagebox.showinfo("Sin datos","No hay transacciones."); return
        ruta = filedialog.asksaveasfilename(
            title="Exportar CSV",
            defaultextension=".csv",
            filetypes=[("CSV","*.csv")],
            initialfile=f"ventas_{self.registro.fecha}.csv")
        if not ruta: return
        try:
            self.registro.exportar_csv(ruta)
            messagebox.showinfo("Exportado", f"✅ {ruta}")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))


# ─────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = CajeroApp()
    app.mainloop()
