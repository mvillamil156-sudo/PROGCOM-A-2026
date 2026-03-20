"""
SINOPSIS
--------
CONCEPTOS CUBIERTOS
-------------------
  Nivel 1 — CLASES Y OBJETOS        : Construye tu héroe atributo a atributo
  Nivel 2 — MÉTODOS                 : Aprende los hechizos ejecutando métodos
  Nivel 3 — HERENCIA                : Elige subclase y hereda poderes del padre
  Nivel 4 — ENCAPSULAMIENTO         : Rompe escudos privados con getters/setters
  Nivel 5 — POLIMORFISMO            : Mismo hechizo, diferentes efectos por tipo
  Nivel 6 — ABSTRACCIÓN (BOSS)      : Enfrenta al Dios del Caos usando todo
"""

# ─────────────────────────────────────────────────────────────────────────────
#  IMPORT
# ─────────────────────────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import ttk, font as tkfont
import random, time, math, json, os, sys
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
#  PALETA VISUAL  
# ─────────────────────────────────────────────────────────────────────────────
C = {
    "bg":        "#0e0e1a",   # fondo oscuro
    "bg2":       "#161628",   # panel secundario
    "bg3":       "#1e1e38",   # panel terciario
    "border":    "#2a2a50",   # bordes
    "amber":     "#f59e0b",   # acento principal
    "amber2":    "#fcd34d",   # acento brillante
    "cyan":      "#06b6d4",   # código / técnico
    "green":     "#10b981",   # éxito / correcto
    "red":       "#ef4444",   # error / daño
    "purple":    "#8b5cf6",   # magia / herencia
    "pink":      "#ec4899",   # polimorfismo
    "white":     "#f1f5f9",   # texto principal
    "gray":      "#94a3b8",   # texto secundario
    "dim":       "#475569",   # texto apagado
    "hp_bar":    "#22c55e",
    "hp_low":    "#ef4444",
    "mp_bar":    "#3b82f6",
    "xp_bar":    "#f59e0b",
}

FONTS = {}  # populated after Tk() init

# ─────────────────────────────────────────────────────────────────────────────
#  ══════════════════════════════════════════════════════════════════════════
#  DOMINIO 
#  ══════════════════════════════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────────────────────

# ┌─────────────────────────────────────────────────────────────────────────┐
# │  CONCEPTO 1 — CLASES Y OBJETOS                                          │
# │  Una clase es un molde. Un objeto es una instancia del molde.           │
# └─────────────────────────────────────────────────────────────────────────┘

class Stat:
    """Atributo numérico con valor actual y máximo — encapsula la lógica."""
    def __init__(self, valor: int, maximo: int = None):
        self._valor  = valor
        self._maximo = maximo if maximo is not None else valor

    @property
    def valor(self) -> int:          return self._valor
    @property
    def maximo(self) -> int:         return self._maximo
    @property
    def porcentaje(self) -> float:   return max(0.0, self._valor / self._maximo)

    def modificar(self, delta: int):
        self._valor = max(0, min(self._maximo, self._valor + delta))

    def restaurar(self):             self._valor = self._maximo
    def esta_vacio(self) -> bool:    return self._valor <= 0
    def __repr__(self):              return f"{self._valor}/{self._maximo}"


class Efecto:
    """Estado alterado sobre un personaje (veneno, bendición, etc.)."""
    def __init__(self, nombre: str, duracion: int, delta_hp: int = 0,
                 delta_atk: int = 0, color: str = "#ffffff"):
        self.nombre    = nombre
        self.duracion  = duracion
        self.delta_hp  = delta_hp
        self.delta_atk = delta_atk
        self.color     = color

    def tick(self, personaje: "Personaje") -> str:
        personaje.hp.modificar(self.delta_hp)
        self.duracion -= 1
        signo = "+" if self.delta_hp >= 0 else ""
        return f"[{self.nombre}] {signo}{self.delta_hp} HP"

    def activo(self) -> bool:
        return self.duracion > 0


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  CONCEPTO 2 — MÉTODOS Y ATRIBUTOS                                       │
# │  Los métodos definen el comportamiento. Los atributos, el estado.       │
# └─────────────────────────────────────────────────────────────────────────┘

class Hechizo:
    """
    Representa una habilidad ejecutable.
    Al instanciar un Hechizo, creas un OBJETO con su propio estado.
    """
    def __init__(self, nombre: str, coste_mp: int, descripcion: str,
                 tipo: str = "dano", color: str = C["amber"], emoji: str = "✨"):
        self.nombre      = nombre
        self.coste_mp    = coste_mp
        self.descripcion = descripcion
        self.tipo        = tipo      # dano | cura | debuff | buff | especial
        self.color       = color
        self.emoji       = emoji
        self._usos       = 0         # atributo privado — encapsulamiento

    # ── Método principal ──────────────────────────────────────────────────
    def ejecutar(self, lanzador: "Personaje", objetivo: "Personaje") -> dict:
        """MÉTODO: acción que modifica estado de objetos."""
        if lanzador.mp.valor < self.coste_mp:
            return {"ok": False, "msg": "✗ MP insuficiente", "dmg": 0}

        lanzador.mp.modificar(-self.coste_mp)
        self._usos += 1
        return self._calcular_efecto(lanzador, objetivo)

    def _calcular_efecto(self, lanzador, objetivo) -> dict:
        """Método protegido — lógica base que las subclases sobreescriben."""
        poder = lanzador.ataque.valor
        dmg   = random.randint(int(poder * 0.8), int(poder * 1.2))
        objetivo.hp.modificar(-dmg)
        return {"ok": True, "msg": f"{self.emoji} {self.nombre}: -{dmg} HP", "dmg": dmg}

    @property
    def usos(self) -> int:
        return self._usos  # getter para atributo privado


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  CONCEPTO 3 — HERENCIA                                                  │
# │  Las subclases heredan y EXTIENDEN la clase padre.                      │
# └─────────────────────────────────────────────────────────────────────────┘

class HechizoDano(Hechizo):
    """Hereda de Hechizo y especializa el cálculo de daño."""
    def __init__(self, nombre, coste_mp, descripcion, multiplicador=1.5, **kw):
        super().__init__(nombre, coste_mp, descripcion, tipo="dano", **kw)
        self.multiplicador = multiplicador   # atributo NUEVO de la subclase

    def _calcular_efecto(self, lanzador, objetivo) -> dict:
        poder = lanzador.ataque.valor
        dmg   = int(random.randint(int(poder), int(poder * 1.4)) * self.multiplicador)
        objetivo.hp.modificar(-dmg)
        return {"ok": True, "msg": f"{self.emoji} {self.nombre}: -{dmg} HP 💥", "dmg": dmg}


class HechizoCura(Hechizo):
    """Hereda de Hechizo — mismo nombre de método, comportamiento diferente."""
    def __init__(self, nombre, coste_mp, descripcion, factor_cura=1.2, **kw):
        super().__init__(nombre, coste_mp, descripcion, tipo="cura", **kw)
        self.factor_cura = factor_cura

    def _calcular_efecto(self, lanzador, objetivo) -> dict:  # POLIMORFISMO aquí
        cura = int(lanzador.magia.valor * self.factor_cura)
        objetivo.hp.modificar(cura)
        return {"ok": True, "msg": f"{self.emoji} {self.nombre}: +{cura} HP 💚", "dmg": -cura}


class HechizoBuff(Hechizo):
    """Aplica efectos temporales — muestra encapsulamiento con Efecto."""
    def __init__(self, nombre, coste_mp, descripcion, efecto: Efecto, **kw):
        super().__init__(nombre, coste_mp, descripcion, tipo="buff", **kw)
        self.efecto = efecto

    def _calcular_efecto(self, lanzador, objetivo) -> dict:
        nuevo_efecto = Efecto(self.efecto.nombre, self.efecto.duracion,
                               self.efecto.delta_hp, self.efecto.delta_atk,
                               self.efecto.color)
        objetivo.efectos.append(nuevo_efecto)
        return {"ok": True, "msg": f"{self.emoji} {self.nombre}: ¡{self.efecto.nombre}!", "dmg": 0}


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  CONCEPTO 4 — CLASE BASE ABSTRACTA: Personaje                           │
# │  Define la INTERFAZ común; las subclases la implementan.                │
# └─────────────────────────────────────────────────────────────────────────┘

class Personaje:
    """
    Clase BASE de todos los personajes del juego.
    Define atributos y métodos comunes.
    No se instancia directamente — es la 'clase abstracta' del juego.
    """
    def __init__(self, nombre: str, hp: int, mp: int,
                 ataque: int, defensa: int, magia: int, emoji: str = "🧙"):
        # ATRIBUTOS DE INSTANCIA — cada objeto tiene los suyos
        self.nombre  = nombre
        self.emoji   = emoji
        # Stats encapsulados en objetos Stat
        self.hp      = Stat(hp)
        self.mp      = Stat(mp)
        self.ataque  = Stat(ataque)
        self.defensa = Stat(defensa)
        self.magia   = Stat(magia)
        self.hechizos: list[Hechizo] = []
        self.efectos:  list[Efecto]  = []
        self._nivel  = 1
        self._xp     = 0

    # ── Métodos comunes ──────────────────────────────────────────────────
    def esta_vivo(self) -> bool:
        return not self.hp.esta_vacio()

    def atacar_basico(self, objetivo: "Personaje") -> dict:
        """Método heredado por TODAS las subclases."""
        poder = self.ataque.valor
        reduccion = objetivo.defensa.valor // 4
        dmg = max(1, random.randint(int(poder * 0.7), poder) - reduccion)
        objetivo.hp.modificar(-dmg)
        return {"ok": True, "msg": f"⚔️ Ataque básico: -{dmg} HP", "dmg": dmg}

    def procesar_efectos(self) -> list[str]:
        """Aplica efectos activos y elimina los expirados."""
        mensajes = []
        for ef in self.efectos:
            mensajes.append(ef.tick(self))
        self.efectos = [ef for ef in self.efectos if ef.activo()]
        return mensajes

    def ganar_xp(self, cantidad: int) -> Optional[str]:
        """Retorna mensaje si sube de nivel."""
        self._xp += cantidad
        umbral = self._nivel * 100
        if self._xp >= umbral:
            self._xp -= umbral
            self._nivel += 1
            self._subir_nivel()
            return f"🌟 ¡{self.nombre} subió al nivel {self._nivel}!"
        return None

    def _subir_nivel(self):
        """Método protegido — las subclases pueden sobreescribir."""
        self.hp.modificar(20)
        self.mp.modificar(10)

    @property
    def nivel(self) -> int:
        return self._nivel

    @property
    def xp(self) -> int:
        return self._xp

    def __str__(self) -> str:
        return f"{self.emoji} {self.nombre} [Nv.{self._nivel}] HP:{self.hp} MP:{self.mp}"


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  CONCEPTO 3 — HERENCIA MÚLTIPLE EN ACCIÓN                               │
# │  Hero → Mago / Guerrero / Pícaro  (árbol de herencia)                   │
# └─────────────────────────────────────────────────────────────────────────┘

class Hero(Personaje):
    """Jugador principal — hereda Personaje y añade progresión."""
    CLASE = "Héroe"
    COLOR = C["amber"]

    def __init__(self, nombre: str):
        # super().__init__() llama al constructor del padre
        super().__init__(nombre, hp=100, mp=60, ataque=18,
                         defensa=12, magia=14, emoji="🧝")
        self.clase       = self.CLASE
        self.oro         = 0
        self.conceptos_aprendidos: list[str] = []

    def _subir_nivel(self):
        """OVERRIDE — sobreescribe el método del padre."""
        super()._subir_nivel()   # llama al padre primero
        self.ataque.modificar(3)
        self.magia.modificar(2)

    def aprender_concepto(self, concepto: str):
        if concepto not in self.conceptos_aprendidos:
            self.conceptos_aprendidos.append(concepto)

    def aprendio(self, concepto: str) -> bool:
        return concepto in self.conceptos_aprendidos


class Mago(Hero):
    """
    Subclase de Hero.  Árbol: Mago → Hero → Personaje
    Hereda TODO de Hero y Personaje, especializa stats y hechizos.
    """
    CLASE = "Mago"
    COLOR = C["purple"]

    def __init__(self, nombre: str):
        super().__init__(nombre)
        self.emoji = "🧙"
        self.clase = "Mago"
        # Reajuste de stats — el mago sacrifica defensa por magia
        self.magia._valor   += 20
        self.magia._maximo  += 20
        self.mp._valor      += 30
        self.mp._maximo     += 30
        self.defensa._valor -= 4
        # Hechizos especiales de la subclase
        self.hechizos = [
            HechizoDano("Bola de Fuego", 15, "Daño mágico explosivo",
                        multiplicador=1.8, color=C["red"], emoji="🔥"),
            HechizoCura("Toque Vital",  10, "Restaura HP propio",
                        factor_cura=1.5, color=C["green"], emoji="💚"),
            HechizoBuff("Arcano Escudo", 12, "Reduce daño recibido por 3 turnos",
                        efecto=Efecto("Escudo Mágico", 3, 0, 5, C["purple"]),
                        color=C["purple"], emoji="🛡️"),
        ]

    def _subir_nivel(self):
        super()._subir_nivel()
        self.magia.modificar(5)   # el mago crece en magia al subir nivel


class Guerrero(Hero):
    """
    Subclase de Hero. Árbol: Guerrero → Hero → Personaje
    Alta defensa y ataque, poca magia.
    """
    CLASE = "Guerrero"
    COLOR = C["amber"]

    def __init__(self, nombre: str):
        super().__init__(nombre)
        self.emoji = "⚔️"
        self.clase = "Guerrero"
        self.ataque._valor  += 15
        self.ataque._maximo += 15
        self.defensa._valor += 10
        self.defensa._maximo+= 10
        self.hp._valor      += 30
        self.hp._maximo     += 30
        self.magia._valor   -= 5
        self.hechizos = [
            HechizoDano("Golpe Brutal",  8, "Ataque físico devastador",
                        multiplicador=2.0, color=C["amber"], emoji="⚔️"),
            HechizoBuff("Furia Berserker", 10, "Aumenta ATK por 2 turnos",
                        efecto=Efecto("Furia", 2, 0, 12, C["red"]),
                        color=C["red"], emoji="😤"),
            HechizoCura("Segundo Aliento", 15, "Recupera 30% del HP máximo",
                        factor_cura=0.8, color=C["green"], emoji="💨"),
        ]

    def _subir_nivel(self):
        super()._subir_nivel()
        self.ataque.modificar(5)
        self.defensa.modificar(3)


class Picaro(Hero):
    """
    Subclase de Hero. Árbol: Pícaro → Hero → Personaje
    Velocidad y veneno como especialidad.
    """
    CLASE = "Pícaro"
    COLOR = C["cyan"]

    def __init__(self, nombre: str):
        super().__init__(nombre)
        self.emoji = "🗡️"
        self.clase = "Pícaro"
        self.ataque._valor  += 8
        self.ataque._maximo += 8
        self.mp._valor      += 15
        self.mp._maximo     += 15
        self._critico = 0.25    # 25% crítico — atributo privado propio
        self.hechizos = [
            HechizoDano("Puñalada Crítica", 10, "Alta probabilidad de crítico",
                        multiplicador=2.5, color=C["cyan"], emoji="🗡️"),
            HechizoBuff("Veneno Mortal", 8, "Aplica veneno por 4 turnos",
                        efecto=Efecto("Veneno", 4, -12, 0, C["green"]),
                        color=C["green"], emoji="☠️"),
            HechizoDano("Sombra Gemela", 18, "Ataca dos veces",
                        multiplicador=1.2, color=C["purple"], emoji="👥"),
        ]

    @property
    def critico(self) -> float:
        return self._critico    # getter del atributo encapsulado


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  CONCEPTO 5 — POLIMORFISMO                                              │
# │  Mismo método, comportamientos distintos según el tipo del objeto.      │
# └─────────────────────────────────────────────────────────────────────────┘

class Enemigo(Personaje):
    """Clase base de enemigos — el método ia() es polimórfico."""

    def __init__(self, nombre, hp, mp, ataque, defensa, magia,
                 emoji, xp_recompensa, oro_recompensa, color, descripcion=""):
        super().__init__(nombre, hp, mp, ataque, defensa, magia, emoji)
        self.xp_recompensa  = xp_recompensa
        self.oro_recompensa = oro_recompensa
        self.color          = color
        self.descripcion    = descripcion

    def ia(self, objetivo: Personaje) -> dict:
        """
        MÉTODO POLIMÓRFICO — cada subclase lo implementa diferente.
        Todos tienen el mismo nombre; cada objeto hace algo distinto.
        """
        return self.atacar_basico(objetivo)

    def concepto_poo(self) -> str:
        return "Clases y Objetos"


class BugSlime(Enemigo):
    """Nivel 1 — enseña Clases."""
    def __init__(self):
        super().__init__("Bug Slime 🟢", 45, 0, 10, 4, 0,
                         "🟢", 30, 5, C["green"],
                         "Un error lógico hecho criatura.")

    def ia(self, objetivo) -> dict:           # POLIMORFISMO
        return self.atacar_basico(objetivo)

    def concepto_poo(self): return "Clases y Objetos"


class NullPointer(Enemigo):
    """Nivel 2 — enseña Métodos."""
    def __init__(self):
        super().__init__("NullPointer 👻", 70, 30, 14, 6, 10,
                         "👻", 55, 10, C["gray"],
                         "Aparece cuando llamas a un método en nada.")
        self.hechizos = [
            HechizoDano("Error Fatal", 10, "Daño de referencia nula",
                        multiplicador=1.6, emoji="💀")
        ]

    def ia(self, objetivo) -> dict:           # POLIMORFISMO
        if self.mp.valor >= 10 and random.random() < 0.6:
            return self.hechizos[0].ejecutar(self, objetivo)
        return self.atacar_basico(objetivo)

    def concepto_poo(self): return "Métodos"


class InheritanceWyrm(Enemigo):
    """Nivel 3 — enseña Herencia."""
    def __init__(self):
        super().__init__("Wyrm de Herencia 🐉", 100, 50, 18, 10, 15,
                         "🐉", 80, 18, C["purple"],
                         "Hereda poderes de todos sus ancestros.")
        self.hechizos = [
            HechizoDano("Llama Ancestral", 15, "Poder heredado",
                        multiplicador=1.7, emoji="🔥"),
            HechizoBuff("Escama Padre",    12, "Buff heredado del padre",
                        efecto=Efecto("Escudo Ancestral", 2, 0, 8, C["purple"]),
                        emoji="🛡️"),
        ]
        self._generacion = 3  # atributo propio

    def ia(self, objetivo) -> dict:           # POLIMORFISMO — IA más compleja
        roll = random.random()
        if self.hp.porcentaje < 0.4:          # cuando está bajo de HP, se defiende
            if self.mp.valor >= 12:
                return self.hechizos[1].ejecutar(self, self)
        if roll < 0.5 and self.mp.valor >= 15:
            return self.hechizos[0].ejecutar(self, objetivo)
        return self.atacar_basico(objetivo)

    def concepto_poo(self): return "Herencia"


class EncapsulatedGolem(Enemigo):
    """Nivel 4 — enseña Encapsulamiento. Tiene escudos privados."""
    def __init__(self):
        super().__init__("Golem Encapsulado 🗿", 120, 40, 20, 25, 8,
                         "🗿", 100, 25, C["amber"],
                         "Sus datos están protegidos. Usa getters para atacar.")
        self.__escudo_privado = 3     # ¡atributo doblemente privado!
        self.hechizos = [
            HechizoDano("Muro de Piedra", 10, "Alta defensa",
                        multiplicador=1.3, emoji="🗿"),
        ]

    @property
    def escudo(self) -> int:
        return self.__escudo_privado   # getter — única forma de acceder

    def romper_escudo(self):
        """Setter — el jugador debe usarlo correctamente."""
        if self.__escudo_privado > 0:
            self.__escudo_privado -= 1
            return True
        return False

    def ia(self, objetivo) -> dict:           # POLIMORFISMO
        if self.__escudo_privado > 0:
            self.defensa._valor = 25 + self.__escudo_privado * 8
        else:
            self.defensa._valor = 8
        if random.random() < 0.4 and self.mp.valor >= 10:
            return self.hechizos[0].ejecutar(self, objetivo)
        return self.atacar_basico(objetivo)

    def concepto_poo(self): return "Encapsulamiento"


class PolymorphDemon(Enemigo):
    """Nivel 5 — enseña Polimorfismo. Cambia de forma."""
    FORMAS = [
        ("Fuego 🔥",  C["red"],    22, 6),
        ("Hielo 🧊",  C["cyan"],   14, 14),
        ("Rayo ⚡",   C["amber2"], 28, 2),
    ]

    def __init__(self):
        super().__init__("Demonio Poli 🎭", 140, 80, 20, 8, 18,
                         "🎭", 130, 35, C["pink"],
                         "Mismo ser, múltiples formas. El polimorfismo encarnado.")
        self._forma_idx = 0
        self.hechizos = [
            HechizoDano("Cambio Polimórfico", 0, "Transforma y ataca",
                        multiplicador=1.9, emoji="🎭"),
            HechizoCura("Regenerar Forma", 20, "Cura al cambiar",
                        factor_cura=0.6, emoji="✨"),
        ]

    def cambiar_forma(self):
        self._forma_idx = (self._forma_idx + 1) % len(self.FORMAS)
        nombre_f, color_f, atk_f, def_f = self.FORMAS[self._forma_idx]
        self.color = color_f
        self.ataque._valor = atk_f
        self.defensa._valor = def_f
        return nombre_f

    def ia(self, objetivo) -> dict:           # POLIMORFISMO — cambia en cada turno
        if random.random() < 0.4:
            nueva_forma = self.cambiar_forma()
            r = self.hechizos[0].ejecutar(self, objetivo)
            r["msg"] = f"🎭 Cambia a forma {nueva_forma}!\n" + r["msg"]
            return r
        if self.hp.porcentaje < 0.35 and self.mp.valor >= 20:
            return self.hechizos[1].ejecutar(self, self)
        return self.atacar_basico(objetivo)

    def concepto_poo(self): return "Polimorfismo"


class ChaosGod(Enemigo):
    """JEFE FINAL — Nivel 6 — usa TODOS los conceptos."""
    def __init__(self):
        super().__init__("Dios del Caos Abstracto ☯️", 200, 150, 28, 15, 25,
                         "☯️", 300, 100, C["red"],
                         "La abstracción personificada. Domina todos los conceptos.")
        self.__fase = 1
        self.hechizos = [
            HechizoDano("Caos Absoluto",   25, "Daño caótico masivo",
                        multiplicador=2.2, color=C["red"], emoji="☯️"),
            HechizoCura("Reconstruir",     30, "Se regenera masivamente",
                        factor_cura=2.0, color=C["purple"], emoji="✨"),
            HechizoBuff("Aura de Caos",    20, "Todos los buffs a la vez",
                        efecto=Efecto("Caos", 3, 5, 10, C["red"]), emoji="🌀"),
        ]

    @property
    def fase(self): return self.__fase  # encapsulado

    def ia(self, objetivo) -> dict:     # POLIMORFISMO extremo — IA en fases
        if self.hp.porcentaje < 0.3 and self.__fase < 3:
            self.__fase = 3
            self.ataque._valor += 10
        elif self.hp.porcentaje < 0.6 and self.__fase < 2:
            self.__fase = 2
            self.ataque._valor += 5

        roll = random.random()
        if self.__fase == 3:
            if roll < 0.5 and self.mp.valor >= 25:
                return self.hechizos[0].ejecutar(self, objetivo)
            if roll < 0.7 and self.mp.valor >= 30:
                return self.hechizos[1].ejecutar(self, self)
        elif self.__fase == 2:
            if roll < 0.4 and self.mp.valor >= 20:
                return self.hechizos[2].ejecutar(self, self)
            if roll < 0.7 and self.mp.valor >= 25:
                return self.hechizos[0].ejecutar(self, objetivo)
        return self.atacar_basico(objetivo)

    def concepto_poo(self): return "Abstracción"


# ─────────────────────────────────────────────────────────────────────────────
#  DATOS DE NIVELES
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class NivelData:
    numero:        int
    titulo:        str
    concepto:      str
    descripcion:   str
    enemigo_clase: type
    color:         str
    quiz_pregunta: str
    quiz_opciones: list[str]
    quiz_correcta: int    # índice 0-based
    quiz_tip:      str
    emoji_concepto: str

NIVELES: list[NivelData] = [
    NivelData(
        1, "El Nacimiento del Código", "Clases y Objetos",
        "Una CLASE es un plano/molde. Un OBJETO es una instancia de ese molde.\n"
        "Cuando escribes:  mi_perro = Perro('Fido', 3)\n"
        "...estás creando un OBJETO 'mi_perro' a partir de la CLASE 'Perro'.",
        BugSlime, C["green"],
        "¿Qué es una CLASE en POO?",
        ["Una función que retorna datos",
         "Un molde/plantilla para crear objetos",
         "Una variable con múltiples valores",
         "Un archivo de configuración"],
        1,
        "💡 Piensa en una clase como un molde de galletas: el molde es la clase, cada galleta es un objeto.",
        "🏗️"
    ),
    NivelData(
        2, "Los Mensajes del Vacío", "Métodos",
        "Los MÉTODOS son funciones definidas dentro de una clase.\n"
        "Definen el COMPORTAMIENTO de los objetos.\n"
        "self siempre es el primer parámetro — refiere al objeto actual.\n"
        "Ej: mi_perro.ladrar()  →  llama al método ladrar() del objeto.",
        NullPointer, C["gray"],
        "¿Qué hace la palabra 'self' en un método de Python?",
        ["Indica que el método es estático",
         "Es obligatoria por razones de sintaxis sin significado real",
         "Referencia al objeto actual (la instancia)",
         "Crea una copia del objeto"],
        2,
        "💡 'self' es como decir 'yo mismo'. mi_perro.ladrar() → Python pasa mi_perro como self automáticamente.",
        "⚙️"
    ),
    NivelData(
        3, "El Linaje del Dragón", "Herencia",
        "La HERENCIA permite que una clase (hija) reutilice atributos\n"
        "y métodos de otra clase (padre).\n"
        "class Perro(Animal):  →  Perro hereda TODO de Animal.\n"
        "super().__init__() llama al constructor del padre.",
        InheritanceWyrm, C["purple"],
        "Si class Gato(Animal): ¿qué significa eso?",
        ["Gato y Animal son clases independientes sin relación",
         "Gato hereda atributos y métodos de Animal",
         "Animal hereda de Gato",
         "Son alias del mismo tipo"],
        1,
        "💡 La herencia es como la genética: el hijo hereda rasgos del padre pero puede tener los suyos propios.",
        "🧬"
    ),
    NivelData(
        4, "El Castillo de Cristal", "Encapsulamiento",
        "El ENCAPSULAMIENTO oculta los datos internos de un objeto.\n"
        "En Python: _atributo = protegido  |  __atributo = privado\n"
        "Los GETTERS (@property) leen datos privados.\n"
        "Los SETTERS (@x.setter) modifican datos privados con validación.",
        EncapsulatedGolem, C["amber"],
        "¿Para qué sirven los getters y setters?",
        ["Para hacer el código más largo",
         "Para acceder/modificar atributos privados con control",
         "Son obligatorios en todas las clases",
         "Sólo para atributos públicos"],
        1,
        "💡 Encapsular es como un cajero: no tocas el dinero directamente, lo haces a través de la interfaz controlada.",
        "🔒"
    ),
    NivelData(
        5, "El Demonio de las Formas", "Polimorfismo",
        "El POLIMORFISMO = 'muchas formas'.\n"
        "El MISMO nombre de método funciona diferente según el objeto.\n"
        "Ej: animal.hablar() → Perro: 'Guau', Gato: 'Miau', Vaca: 'Muu'\n"
        "Mismo método, objetos diferentes, comportamientos distintos.",
        PolymorphDemon, C["pink"],
        "¿Qué es el polimorfismo en POO?",
        ["Usar múltiples clases sin relación entre sí",
         "Mismo método con diferentes implementaciones según el objeto",
         "Crear objetos dentro de otros objetos",
         "Copiar código entre clases"],
        1,
        "💡 Polimorfismo = muchas formas. Un control remoto (mismo método 'presionar') funciona diferente en cada aparato.",
        "🎭"
    ),
    NivelData(
        6, "El Caos Abstracto", "Abstracción",
        "La ABSTRACCIÓN simplifica la complejidad.\n"
        "Mostramos solo lo esencial y ocultamos los detalles.\n"
        "Las clases abstractas (ABC) definen métodos que las subclases DEBEN implementar.\n"
        "¡Has aprendido los 4 pilares de la POO!",
        ChaosGod, C["red"],
        "¿Cuáles son los 4 pilares de la POO?",
        ["Variables, Funciones, Bucles, Condicionales",
         "Clases, Métodos, Imports, Módulos",
         "Encapsulamiento, Herencia, Polimorfismo, Abstracción",
         "Público, Privado, Protegido, Estático"],
        2,
        "💡 Los 4 pilares son: Encapsulamiento (ocultar), Herencia (reutilizar), Polimorfismo (muchas formas), Abstracción (simplificar).",
        "🌌"
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
#  GESTOR DE ESTADO DEL JUEGO
# ─────────────────────────────────────────────────────────────────────────────

class GameState:
    """Gestiona el estado global de la partida."""
    def __init__(self):
        self.hero:     Optional[Hero]    = None
        self.enemigo:  Optional[Enemigo] = None
        self.nivel_idx = 0
        self.fase      = "menu"       # menu|nombre|clase|tutorial|batalla|quiz|victoria|gameover|fin
        self.log:      list[str]      = []
        self.turno     = 0
        self.puntaje   = 0
        self.racha_correctas = 0
        self.tiempo_inicio = time.time()

    @property
    def nivel_actual(self) -> NivelData:
        return NIVELES[min(self.nivel_idx, len(NIVELES)-1)]

    def log_add(self, msg: str, color: str = C["white"]):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log.append((f"[{ts}] {msg}", color))
        if len(self.log) > 200:
            self.log.pop(0)

    def cargar_nivel(self):
        nd = self.nivel_actual
        self.enemigo = nd.enemigo_clase()
        self.turno   = 0

    def es_ultimo_nivel(self) -> bool:
        return self.nivel_idx >= len(NIVELES) - 1


# ─────────────────────────────────────────────────────────────────────────────
#  ══════════════════════════════════════════════════════════════════════════
#  INTERFAZ GRÁFICA
#  ══════════════════════════════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────────────────────

def _hex_color(widget, color: str):
    """Aplica color de fondo a un widget."""
    try: widget.config(bg=color)
    except: pass


class OOPQuestApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("OOP Quest — El RPG de la Programación Orientada a Objetos")
        self.configure(bg=C["bg"])
        self.geometry("1100x780")
        self.minsize(900, 650)
        self.resizable(True, True)

        self._init_fonts()
        self.state = GameState()
        self._anim_ids = []   # ids de animaciones pendientes

        self._build_layout()
        self._show_menu()

    # ── FUENTES ─────────────────────────────────────────────────────────────
    def _init_fonts(self):
        global FONTS
        FONTS = {
            "title":   tkfont.Font(family="Georgia", size=26, weight="bold"),
            "h1":      tkfont.Font(family="Georgia", size=18, weight="bold"),
            "h2":      tkfont.Font(family="Georgia", size=14, weight="bold"),
            "h3":      tkfont.Font(family="Helvetica", size=11, weight="bold"),
            "body":    tkfont.Font(family="Helvetica", size=10),
            "mono":    tkfont.Font(family="Courier New", size=10),
            "mono_sm": tkfont.Font(family="Courier New", size=8),
            "lg":      tkfont.Font(family="Helvetica", size=13),
            "emoji":   tkfont.Font(family="Segoe UI Emoji", size=28),
            "sm":      tkfont.Font(family="Helvetica", size=9),
        }

    # ── LAYOUT PRINCIPAL ────────────────────────────────────────────────────
    def _build_layout(self):
        """Marco estructural permanente."""
        # Barra superior
        self.topbar = tk.Frame(self, bg=C["bg2"], height=50)
        self.topbar.pack(fill=tk.X)
        self.topbar.pack_propagate(False)

        self._lbl_title = tk.Label(self.topbar, text="⚔️  OOP Quest",
                                   bg=C["bg2"], fg=C["amber"],
                                   font=FONTS["h2"])
        self._lbl_title.pack(side=tk.LEFT, padx=16, pady=10)

        self._lbl_nivel_top = tk.Label(self.topbar, text="",
                                        bg=C["bg2"], fg=C["gray"],
                                        font=FONTS["sm"])
        self._lbl_nivel_top.pack(side=tk.LEFT, padx=8)

        self._lbl_puntaje = tk.Label(self.topbar, text="",
                                      bg=C["bg2"], fg=C["amber2"],
                                      font=FONTS["h3"])
        self._lbl_puntaje.pack(side=tk.RIGHT, padx=16)

        tk.Frame(self, bg=C["border"], height=1).pack(fill=tk.X)

        # Área de contenido (dinámica)
        self.content = tk.Frame(self, bg=C["bg"])
        self.content.pack(fill=tk.BOTH, expand=True)

    def _clear_content(self):
        """Limpia el área de contenido."""
        for aid in self._anim_ids:
            try: self.after_cancel(aid)
            except: pass
        self._anim_ids.clear()
        for w in self.content.winfo_children():
            w.destroy()

    # ── HELPERS UI ──────────────────────────────────────────────────────────
    def _make_button(self, parent, text, cmd, color=None, fg=C["bg"],
                     width=None, font=None, pady=8):
        color = color or C["amber"]
        font  = font  or FONTS["h3"]
        kw = {"width": width} if width else {}
        b = tk.Button(parent, text=text, command=cmd,
                      bg=color, fg=fg, relief="flat",
                      font=font, padx=16, pady=pady,
                      activebackground=color, activeforeground=fg,
                      cursor="hand2", **kw)
        b.bind("<Enter>", lambda e, c=color: b.config(bg=self._lighten(c, 0.2)))
        b.bind("<Leave>", lambda e, c=color: b.config(bg=c))
        return b

    @staticmethod
    def _lighten(hex_color: str, factor: float) -> str:
        h = hex_color.lstrip("#")
        r,g,b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        r = min(255, int(r + (255-r)*factor))
        g = min(255, int(g + (255-g)*factor))
        b = min(255, int(b + (255-b)*factor))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _bar(self, parent, value: float, color: str, width=180, height=14) -> tk.Canvas:
        cv = tk.Canvas(parent, width=width, height=height,
                       bg=C["bg3"], highlightthickness=1,
                       highlightbackground=C["border"])
        fill_w = max(2, int(width * value))
        cv.create_rectangle(2, 2, fill_w, height-2, fill=color, outline="")
        return cv

    def _section(self, parent, title: str, color=None) -> tk.Frame:
        color = color or C["amber"]
        hdr = tk.Frame(parent, bg=C["bg2"])
        hdr.pack(fill=tk.X, pady=(8,0))
        tk.Frame(hdr, bg=color, width=4).pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(hdr, text=f" {title}", bg=C["bg2"], fg=color,
                 font=FONTS["h3"]).pack(side=tk.LEFT, padx=6, pady=4)
        body = tk.Frame(parent, bg=C["bg2"], padx=8, pady=6)
        body.pack(fill=tk.X)
        return body

    # ─────────────────────────────────────────────────────────────────────
    #  PANTALLAS
    # ─────────────────────────────────────────────────────────────────────

    # ── MENÚ PRINCIPAL ──────────────────────────────────────────────────
    def _show_menu(self):
        self._clear_content()
        self.state.fase = "menu"
        self._lbl_nivel_top.config(text="")
        self._lbl_puntaje.config(text="")

        f = tk.Frame(self.content, bg=C["bg"])
        f.pack(expand=True)

        # Título animado
        title_frame = tk.Frame(f, bg=C["bg"])
        title_frame.pack(pady=(40,0))

        tk.Label(title_frame, text="⚔️", bg=C["bg"],
                 font=FONTS["emoji"]).pack()

        tk.Label(title_frame, text="OOP QUEST",
                 bg=C["bg"], fg=C["amber"],
                 font=FONTS["title"]).pack()

        tk.Label(title_frame,
                 text="El RPG donde programar ES el combate",
                 bg=C["bg"], fg=C["gray"],
                 font=FONTS["lg"]).pack(pady=(4,0))

        # Conceptos badge
        badges_f = tk.Frame(f, bg=C["bg"])
        badges_f.pack(pady=20)
        conceptos = [
            ("🏗️ Clases", C["green"]),
            ("⚙️ Métodos", C["gray"]),
            ("🧬 Herencia", C["purple"]),
            ("🔒 Encapsulamiento", C["amber"]),
            ("🎭 Polimorfismo", C["pink"]),
            ("🌌 Abstracción", C["red"]),
        ]
        for i, (texto, color) in enumerate(conceptos):
            badge = tk.Label(badges_f, text=texto, bg=color, fg=C["bg"],
                             font=FONTS["sm"], padx=8, pady=4,
                             relief="flat")
            badge.grid(row=i//3, column=i%3, padx=5, pady=4, sticky="ew")

        # Separador
        tk.Frame(f, bg=C["border"], height=1, width=400).pack(pady=20)

        # Botones
        btns = tk.Frame(f, bg=C["bg"])
        btns.pack(pady=8)

        self._make_button(btns, "▶  NUEVA AVENTURA",
                          self._show_nombre, C["amber"], width=22).pack(pady=6)
        self._make_button(btns, "📖  CÓMO JUGAR",
                          self._show_tutorial_global, C["bg2"], C["white"],
                          width=22).pack(pady=6)

        tk.Label(f,
                 text="Aprende los 4 pilares de la POO en 6 batallas épicas",
                 bg=C["bg"], fg=C["dim"], font=FONTS["sm"]).pack(pady=(20,0))
        tk.Label(f,
                 text="Obra original — MIT License — Sin derechos de autor de terceros",
                 bg=C["bg"], fg=C["dim"], font=FONTS["sm"]).pack(pady=(2,0))

    # ── INGRESO DE NOMBRE ───────────────────────────────────────────────
    def _show_nombre(self):
        self._clear_content()

        f = tk.Frame(self.content, bg=C["bg"])
        f.pack(expand=True)

        tk.Label(f, text="¿Cómo se llama tu héroe?",
                 bg=C["bg"], fg=C["amber"], font=FONTS["h1"]).pack(pady=(40,8))
        tk.Label(f, text="Este será tu objeto Hero instanciado en el juego.",
                 bg=C["bg"], fg=C["gray"], font=FONTS["body"]).pack(pady=(0,24))

        # Código visual
        code_f = tk.Frame(f, bg=C["bg3"], padx=16, pady=12)
        code_f.pack(padx=40, fill=tk.X)
        self._code_lbl = tk.Label(code_f,
                                   text='hero = Hero("___")',
                                   bg=C["bg3"], fg=C["cyan"],
                                   font=FONTS["mono"])
        self._code_lbl.pack()

        # Entry
        self._nombre_var = tk.StringVar(value="Pythón")
        entry_f = tk.Frame(f, bg=C["bg"])
        entry_f.pack(pady=20)
        entry = tk.Entry(entry_f, textvariable=self._nombre_var,
                         font=FONTS["h2"], width=18,
                         bg=C["bg3"], fg=C["white"],
                         insertbackground=C["amber"],
                         relief="solid", bd=1,
                         highlightthickness=2,
                         highlightcolor=C["amber"],
                         highlightbackground=C["border"])
        entry.pack(ipady=8)
        entry.focus_set()
        entry.select_range(0, tk.END)

        def on_key(*_):
            n = self._nombre_var.get() or "___"
            self._code_lbl.config(text=f'hero = Hero("{n}")')

        self._nombre_var.trace_add("write", on_key)

        self._make_button(f, "Continuar →", self._show_clase, C["amber"]).pack(pady=8)
        self._make_button(f, "◀ Volver", self._show_menu,
                          C["bg2"], C["gray"]).pack(pady=2)
        entry.bind("<Return>", lambda e: self._show_clase())

    # ── ELECCIÓN DE CLASE ───────────────────────────────────────────────
    def _show_clase(self):
        nombre = self._nombre_var.get().strip() or "Pythón"
        self._clear_content()

        f = tk.Frame(self.content, bg=C["bg"])
        f.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(f, text=f"Elige tu subclase, {nombre}",
                 bg=C["bg"], fg=C["amber"], font=FONTS["h1"]).pack(pady=(0,4))
        tk.Label(f,
                 text="Cada clase HEREDA de Hero. Observa cómo la herencia cambia los stats.",
                 bg=C["bg"], fg=C["gray"], font=FONTS["body"]).pack(pady=(0,16))

        # Diagrama de herencia
        diag = tk.Frame(f, bg=C["bg2"], padx=12, pady=8)
        diag.pack(fill=tk.X, pady=(0,16))
        tk.Label(diag,
                 text="Árbol de herencia:  Personaje  →  Hero  →  { Mago | Guerrero | Pícaro }",
                 bg=C["bg2"], fg=C["cyan"], font=FONTS["mono"]).pack()

        # Cards de clases
        cards_f = tk.Frame(f, bg=C["bg"])
        cards_f.pack(fill=tk.BOTH, expand=True)
        cards_f.columnconfigure(0, weight=1)
        cards_f.columnconfigure(1, weight=1)
        cards_f.columnconfigure(2, weight=1)

        clases = [
            (Mago,     "🧙 Mago",     "HP:100 MP:90  ATK:18 DEF:8  MAG:34",
             C["purple"], "Especialista en magia.\nAlta magia, baja defensa.\nHechizos: Bola de Fuego,\nToque Vital, Arcano Escudo"),
            (Guerrero, "⚔️ Guerrero", "HP:130 MP:60  ATK:33 DEF:22 MAG:9",
             C["amber"],  "Maestro del combate físico.\nAlto HP y ATK.\nHechizos: Golpe Brutal,\nFuria Berserker, 2do Aliento"),
            (Picaro,   "🗡️ Pícaro",   "HP:100 MP:75  ATK:26 DEF:12 MAG:14",
             C["cyan"],   "Velocidad y veneno.\n25% de golpe crítico.\nHechizos: Puñalada Crítica,\nVeneno Mortal, Sombra Gemela"),
        ]

        for i, (cls, titulo, stats, color, desc) in enumerate(clases):
            card = tk.Frame(cards_f, bg=C["bg2"], bd=2, relief="solid",
                            highlightbackground=color, highlightthickness=2)
            card.grid(row=0, column=i, padx=8, pady=4, sticky="nsew")

            tk.Label(card, text=titulo, bg=C["bg2"], fg=color,
                     font=FONTS["h2"]).pack(pady=(12,4))
            tk.Label(card, text=stats, bg=C["bg2"], fg=C["cyan"],
                     font=FONTS["mono_sm"]).pack(pady=2)
            tk.Frame(card, bg=C["border"], height=1).pack(fill=tk.X, pady=6)
            tk.Label(card, text=desc, bg=C["bg2"], fg=C["gray"],
                     font=FONTS["sm"], justify="left").pack(padx=12, pady=(0,8))

            tk.Label(card, text="class {} (Hero):".format(cls.CLASE),
                     bg=C["bg3"], fg=C["purple"],
                     font=FONTS["mono_sm"]).pack(fill=tk.X, padx=4, pady=(4,8))

            self._make_button(card, f"Elegir {cls.CLASE}",
                              lambda c=cls, n=nombre: self._iniciar_juego(n, c),
                              color).pack(pady=(0,12), padx=12, fill=tk.X)

        self._make_button(f, "◀ Volver", self._show_nombre,
                          C["bg2"], C["gray"]).pack(pady=8)

    # ── TUTORIAL GLOBAL ─────────────────────────────────────────────────
    def _show_tutorial_global(self):
        self._clear_content()
        f = tk.Frame(self.content, bg=C["bg"])
        f.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        tk.Label(f, text="📖 Cómo jugar OOP Quest",
                 bg=C["bg"], fg=C["amber"], font=FONTS["h1"]).pack(pady=(0,16))

        secciones = [
            ("🎮 Mecánica de batalla", C["amber"],
             "• Cada nivel presenta un CONCEPTO de POO y un enemigo temático.\n"
             "• PRIMERO: Lee la lección sobre el concepto POO del nivel.\n"
             "• LUEGO: Combate contra el enemigo usando tus hechizos.\n"
             "• FINALMENTE: Responde un quiz para consolidar el aprendizaje."),
            ("⚔️ Combate", C["cyan"],
             "• Ataque Básico: siempre disponible, sin costo de MP.\n"
             "• Hechizos: consumen MP. Cada clase tiene 3 únicos.\n"
             "• El enemigo ataca al final de cada turno tuyo.\n"
             "• Gana XP y Oro al derrotar enemigos."),
            ("📚 Los 4 Pilares (6 niveles)", C["purple"],
             "Nivel 1: Clases y Objetos → Bug Slime\n"
             "Nivel 2: Métodos         → NullPointer\n"
             "Nivel 3: Herencia        → Wyrm de Herencia\n"
             "Nivel 4: Encapsulamiento → Golem Encapsulado\n"
             "Nivel 5: Polimorfismo    → Demonio Polimórfico\n"
             "Nivel 6: Abstracción     → Dios del Caos (Jefe Final)"),
            ("💡 Consejos", C["green"],
             "• Gestiona bien tu MP — los hechizos son más poderosos.\n"
             "• Los buffs son cruciales para sobrevivir al jefe.\n"
             "• Lee las lecciones antes de combatir — el quiz da XP extra.\n"
             "• Los efectos de estado (veneno, furia) son acumulativos."),
        ]

        for titulo, color, texto in secciones:
            sf = self._section(f, titulo, color)
            tk.Label(sf, text=texto, bg=C["bg2"], fg=C["white"],
                     font=FONTS["body"], justify="left").pack(anchor="w")

        self._make_button(f, "◀ Volver al Menú", self._show_menu, C["amber"]).pack(pady=16)

    # ── INICIAR JUEGO ───────────────────────────────────────────────────
    def _iniciar_juego(self, nombre: str, clase: type):
        hero = clase(nombre)
        self.state.hero    = hero
        self.state.nivel_idx = 0
        self.state.puntaje   = 0
        self.state.racha_correctas = 0
        self.state.log.clear()
        self._cargar_nivel()

    def _cargar_nivel(self):
        self.state.cargar_nivel()
        nd = self.state.nivel_actual
        self._lbl_nivel_top.config(
            text=f"Nivel {nd.numero}/6 — {nd.titulo}  |  Concepto: {nd.concepto}")
        self._lbl_puntaje.config(text=f"⭐ {self.state.puntaje} pts")
        self._show_leccion()

    # ── LECCIÓN PRE-BATALLA ─────────────────────────────────────────────
    def _show_leccion(self):
        self._clear_content()
        nd   = self.state.nivel_actual
        hero = self.state.hero

        # Layout: izquierda lección, derecha enemigo
        main = tk.Frame(self.content, bg=C["bg"])
        main.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(main, bg=C["bg"], padx=20, pady=16)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right = tk.Frame(main, bg=C["bg2"], padx=16, pady=16, width=280)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        right.pack_propagate(False)

        # ── Columna izquierda: lección ──
        nivel_badge = tk.Label(left,
                                text=f"  {nd.emoji_concepto}  Nivel {nd.numero} — {nd.concepto}  ",
                                bg=nd.color, fg=C["bg"],
                                font=FONTS["h3"])
        nivel_badge.pack(anchor="w", pady=(0,8))

        tk.Label(left, text=nd.titulo,
                 bg=C["bg"], fg=C["amber"], font=FONTS["h1"]).pack(anchor="w")

        tk.Frame(left, bg=C["border"], height=1).pack(fill=tk.X, pady=8)

        # Descripción / lección
        lec_frame = tk.Frame(left, bg=C["bg3"], padx=16, pady=14)
        lec_frame.pack(fill=tk.X, pady=(0,10))
        tk.Label(lec_frame, text="📚 CONCEPTO:",
                 bg=C["bg3"], fg=nd.color, font=FONTS["h3"]).pack(anchor="w")
        tk.Label(lec_frame, text=nd.descripcion,
                 bg=C["bg3"], fg=C["white"],
                 font=FONTS["mono"], justify="left",
                 wraplength=480).pack(anchor="w", pady=(4,0))

        # Ejemplo código dinámico por nivel
        code_examples = {
            1: ('class Personaje:\n'
                '    def __init__(self, nombre, hp):\n'
                '        self.nombre = nombre  # atributo\n'
                '        self.hp = hp\n\n'
                '# Instanciar = crear OBJETO\n'
                f'heroe = Personaje("{hero.nombre}", 100)'),
            2: ('class Personaje:\n'
                '    def atacar(self):  # MÉTODO\n'
                '        return self.ataque * 1.5\n\n'
                f'# Llamar método en objeto\n'
                f'{hero.nombre.lower()}.atacar()  # → ejecuta comportamiento'),
            3: ('class Hero(Personaje):  # Hereda Personaje\n'
                f'    pass\n\n'
                f'class {hero.clase}(Hero):  # Hereda Hero\n'
                f'    def __init__(self, nombre):\n'
                f'        super().__init__(nombre)  # llama al padre'),
            4: ('class Personaje:\n'
                '    def __init__(self):\n'
                '        self.__vida = 100  # PRIVADO\n\n'
                '    @property\n'
                '    def vida(self):      # GETTER\n'
                '        return self.__vida\n\n'
                '    @vida.setter\n'
                '    def vida(self, v):   # SETTER\n'
                '        self.__vida = max(0, v)'),
            5: ('# MISMO MÉTODO, diferentes comportamientos\n'
                'def hablar(animal):\n'
                '    animal.hablar()  # polimorfismo\n\n'
                'perro.hablar()  → "¡Guau!"\n'
                'gato.hablar()   → "¡Miau!"\n'
                'vaca.hablar()   → "¡Muu!"'),
            6: ('from abc import ABC, abstractmethod\n\n'
                'class Personaje(ABC):  # Abstracta\n'
                '    @abstractmethod\n'
                '    def atacar(self): ...\n\n'
                '# Subclase DEBE implementar atacar()\n'
                f'class {hero.clase}(Personaje):\n'
                f'    def atacar(self): ...'),
        }
        code_f = tk.Frame(left, bg="#0a0a16", padx=12, pady=10,
                          highlightthickness=1, highlightbackground=C["border"])
        code_f.pack(fill=tk.X, pady=(0,12))
        tk.Label(code_f, text="// Python",
                 bg="#0a0a16", fg=C["dim"], font=FONTS["sm"]).pack(anchor="e")
        tk.Label(code_f,
                 text=code_examples.get(nd.numero, ""),
                 bg="#0a0a16", fg=C["cyan"],
                 font=FONTS["mono"], justify="left").pack(anchor="w")

        self._make_button(left, f"⚔️  ¡Al combate contra {self.state.enemigo.nombre}!",
                          self._show_batalla, nd.color).pack(anchor="w", pady=4)

        # ── Columna derecha: enemigo ──
        tk.Label(right, text="ENEMIGO",
                 bg=C["bg2"], fg=C["dim"], font=FONTS["sm"]).pack()
        tk.Label(right, text=self.state.enemigo.emoji,
                 bg=C["bg2"], font=FONTS["emoji"]).pack(pady=4)
        tk.Label(right, text=self.state.enemigo.nombre,
                 bg=C["bg2"], fg=self.state.enemigo.color,
                 font=FONTS["h3"], wraplength=220).pack()
        tk.Label(right, text=self.state.enemigo.descripcion,
                 bg=C["bg2"], fg=C["gray"], font=FONTS["sm"],
                 wraplength=220, justify="center").pack(pady=4)

        tk.Frame(right, bg=C["border"], height=1).pack(fill=tk.X, pady=8)

        tk.Label(right, text="Concepto que enseña:",
                 bg=C["bg2"], fg=C["dim"], font=FONTS["sm"]).pack()
        badge = tk.Label(right,
                          text=f"  {nd.emoji_concepto}  {self.state.enemigo.concepto_poo()}  ",
                          bg=nd.color, fg=C["bg"], font=FONTS["h3"])
        badge.pack(pady=4)

        # Stats del héroe
        tk.Frame(right, bg=C["border"], height=1).pack(fill=tk.X, pady=8)
        tk.Label(right, text=f"TU HÉROE: {hero.emoji} {hero.nombre}",
                 bg=C["bg2"], fg=C["white"], font=FONTS["h3"]).pack()
        tk.Label(right, text=f"Clase: {hero.clase}",
                 bg=C["bg2"], fg=hero.COLOR, font=FONTS["sm"]).pack()

        for stat_name, stat, color in [
            (f"HP {hero.hp}", hero.hp, C["hp_bar"]),
            (f"MP {hero.mp}", hero.mp, C["mp_bar"]),
        ]:
            sf = tk.Frame(right, bg=C["bg2"])
            sf.pack(fill=tk.X, pady=2)
            tk.Label(sf, text=stat_name, bg=C["bg2"], fg=C["gray"],
                     font=FONTS["sm"], width=12, anchor="w").pack(side=tk.LEFT)
            self._bar(sf, stat.porcentaje, color, width=100, height=10).pack(side=tk.LEFT)

    # ── BATALLA ─────────────────────────────────────────────────────────
    def _show_batalla(self):
        self._clear_content()
        hero    = self.state.hero
        enemigo = self.state.enemigo
        nd      = self.state.nivel_actual

        # ── Layout batalla ──
        # TOP: stats de ambos
        # MID: log de batalla
        # BOT: acciones del héroe

        top = tk.Frame(self.content, bg=C["bg"], padx=12, pady=8)
        top.pack(fill=tk.X)

        mid = tk.Frame(self.content, bg=C["bg"])
        mid.pack(fill=tk.BOTH, expand=True, padx=12)

        bot = tk.Frame(self.content, bg=C["bg2"], padx=12, pady=10)
        bot.pack(fill=tk.X, side=tk.BOTTOM)

        # ── Stats frames ──
        hero_f   = tk.Frame(top, bg=C["bg3"], padx=12, pady=8,
                            highlightthickness=2,
                            highlightbackground=hero.COLOR)
        enemy_f  = tk.Frame(top, bg=C["bg3"], padx=12, pady=8,
                            highlightthickness=2,
                            highlightbackground=enemigo.color)

        hero_f.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,6))
        enemy_f.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6,0))

        # Función para actualizar stats
        def update_stats():
            for w in hero_f.winfo_children():   w.destroy()
            for w in enemy_f.winfo_children():  w.destroy()

            # Héroe
            hf = tk.Frame(hero_f, bg=C["bg3"])
            hf.pack(fill=tk.X)
            tk.Label(hf, text=f"{hero.emoji} {hero.nombre} [{hero.clase}] Nv.{hero.nivel}",
                     bg=C["bg3"], fg=hero.COLOR, font=FONTS["h3"]).pack(side=tk.LEFT)

            for lbl_txt, stat, color in [
                (f"HP {hero.hp}", hero.hp, C["hp_bar"] if hero.hp.porcentaje > 0.3 else C["hp_low"]),
                (f"MP {hero.mp}", hero.mp, C["mp_bar"]),
                (f"XP {hero.xp}/{hero.nivel*100}", Stat(hero.xp, hero.nivel*100), C["xp_bar"]),
            ]:
                rf = tk.Frame(hero_f, bg=C["bg3"])
                rf.pack(fill=tk.X, pady=1)
                tk.Label(rf, text=lbl_txt, bg=C["bg3"], fg=C["gray"],
                         font=FONTS["sm"], width=16, anchor="w").pack(side=tk.LEFT)
                self._bar(rf, stat.porcentaje, color, width=140, height=10).pack(side=tk.LEFT)

            # Efectos del héroe
            if hero.efectos:
                ef_txt = "  ".join(f"{e.color[1:3]}●{e.nombre}({e.duracion})" for e in hero.efectos)
                tk.Label(hero_f, text=ef_txt[:60], bg=C["bg3"], fg=C["amber"],
                         font=FONTS["sm"]).pack(anchor="w")

            # Enemigo
            ef2 = tk.Frame(enemy_f, bg=C["bg3"])
            ef2.pack(fill=tk.X)
            tk.Label(ef2, text=f"{enemigo.emoji} {enemigo.nombre}",
                     bg=C["bg3"], fg=enemigo.color, font=FONTS["h3"]).pack(side=tk.LEFT)

            for lbl_txt2, stat2, color2 in [
                (f"HP {enemigo.hp}", enemigo.hp,
                 C["hp_bar"] if enemigo.hp.porcentaje > 0.3 else C["hp_low"]),
                (f"MP {enemigo.mp}", enemigo.mp, C["mp_bar"]),
            ]:
                rf2 = tk.Frame(enemy_f, bg=C["bg3"])
                rf2.pack(fill=tk.X, pady=1)
                tk.Label(rf2, text=lbl_txt2, bg=C["bg3"], fg=C["gray"],
                         font=FONTS["sm"], width=14, anchor="w").pack(side=tk.LEFT)
                self._bar(rf2, stat2.porcentaje, color2, width=140, height=10).pack(side=tk.LEFT)

            if isinstance(enemigo, EncapsulatedGolem):
                tk.Label(enemy_f, text=f"🛡️ Escudos privados: {enemigo.escudo}",
                         bg=C["bg3"], fg=C["amber"], font=FONTS["sm"]).pack(anchor="w")
            if isinstance(enemigo, PolymorphDemon):
                forma = enemigo.FORMAS[enemigo._forma_idx][0]
                tk.Label(enemy_f, text=f"Forma actual: {forma}",
                         bg=C["bg3"], fg=C["pink"], font=FONTS["sm"]).pack(anchor="w")
            if isinstance(enemigo, ChaosGod):
                tk.Label(enemy_f, text=f"⚡ Fase {enemigo.fase}/3",
                         bg=C["bg3"], fg=C["red"], font=FONTS["sm"]).pack(anchor="w")
            if enemigo.efectos:
                ef_txt2 = "  ".join(f"{e.nombre}({e.duracion})" for e in enemigo.efectos)
                tk.Label(enemy_f, text=ef_txt2[:50], bg=C["bg3"], fg=C["pink"],
                         font=FONTS["sm"]).pack(anchor="w")

        update_stats()

        # ── Log de batalla ──
        log_frame = tk.Frame(mid, bg=C["bg2"])
        log_frame.pack(fill=tk.BOTH, expand=True, pady=6)

        log_canvas = tk.Canvas(log_frame, bg=C["bg2"], highlightthickness=0)
        log_sb     = ttk.Scrollbar(log_frame, orient="vertical",
                                   command=log_canvas.yview)
        log_canvas.configure(yscrollcommand=log_sb.set)
        log_sb.pack(side=tk.RIGHT, fill=tk.Y)
        log_canvas.pack(fill=tk.BOTH, expand=True)

        self._log_inner = tk.Frame(log_canvas, bg=C["bg2"])
        self._log_win   = log_canvas.create_window((0,0), window=self._log_inner,
                                                    anchor="nw")
        self._log_inner.bind("<Configure>",
            lambda e: log_canvas.configure(scrollregion=log_canvas.bbox("all")))
        log_canvas.bind("<Configure>",
            lambda e: log_canvas.itemconfig(self._log_win, width=e.width))
        self._log_canvas_ref = log_canvas

        # Mensaje inicial
        self.state.log_add(f"⚔️ ¡Comienza el Nivel {nd.numero}: {nd.titulo}!", nd.color)
        self.state.log_add(f"Concepto: {nd.concepto}", nd.color)
        self.state.log_add(f"Tu héroe {hero.nombre} enfrenta a {enemigo.nombre}!", C["white"])
        self._render_log()

        def _log_add_render(msg, color=C["white"]):
            self.state.log_add(msg, color)
            self._render_log()

        # ── Botones de acción ──
        def rebuild_actions():
            for w in bot.winfo_children(): w.destroy()

            tk.Label(bot, text="⚔️ TU TURNO:", bg=C["bg2"],
                     fg=C["amber"], font=FONTS["h3"]).pack(side=tk.LEFT, padx=(0,10))

            # Ataque básico
            self._make_button(bot, "⚔️ Atacar",
                              lambda: do_action("basico"),
                              C["bg3"], C["white"], font=FONTS["body"]).pack(side=tk.LEFT, padx=4)

            # Hechizos
            for i, h in enumerate(hero.hechizos):
                color_h = h.color if hero.mp.valor >= h.coste_mp else C["dim"]
                lbl_h   = f"{h.emoji} {h.nombre}\n(MP:{h.coste_mp})"
                self._make_button(bot, lbl_h,
                                  lambda idx=i: do_action("hechizo", idx),
                                  color_h, C["bg"] if color_h != C["dim"] else C["dim"],
                                  font=FONTS["sm"]).pack(side=tk.LEFT, padx=4)

            # Acción especial vs Golem
            if isinstance(enemigo, EncapsulatedGolem) and enemigo.escudo > 0:
                self._make_button(bot, f"🔑 Romper Escudo\n(getter/setter)",
                                  lambda: do_action("especial"),
                                  C["amber"], C["bg"],
                                  font=FONTS["sm"]).pack(side=tk.LEFT, padx=4)

        def do_action(tipo: str, idx: int = 0):
            if not hero.esta_vivo() or not enemigo.esta_vivo():
                return

            self.state.turno += 1
            msgs = []

            # ── TURNO DEL HÉROE ──
            if tipo == "basico":
                r = hero.atacar_basico(enemigo)
                msgs.append((r["msg"], C["amber"]))
            elif tipo == "hechizo":
                hechizo = hero.hechizos[idx]
                r = hechizo.ejecutar(hero, enemigo)
                color_m = C["green"] if hechizo.tipo == "cura" else C["red"]
                msgs.append((r["msg"], color_m if r["ok"] else C["dim"]))
            elif tipo == "especial":
                if isinstance(enemigo, EncapsulatedGolem):
                    if enemigo.romper_escudo():
                        msgs.append((f"🔑 ¡Escudo privado roto! Quedan {enemigo.escudo}",
                                     C["amber"]))
                        hero.ganar_xp(15)
                    else:
                        msgs.append(("❌ No hay escudos que romper", C["dim"]))

            # Efectos del héroe
            for em in hero.procesar_efectos():
                msgs.append((em, C["cyan"]))

            # ── TURNO DEL ENEMIGO ──
            if enemigo.esta_vivo():
                r_e = enemigo.ia(hero)
                msgs.append((f"🔴 {enemigo.nombre}: {r_e['msg']}", enemigo.color))
                # Efectos del enemigo
                for em in enemigo.procesar_efectos():
                    msgs.append((f"  {em}", C["gray"]))

            # XP por daño
            total_dmg = sum(abs(m[0].count("-")) * 5 for m in msgs)
            xp_msg = hero.ganar_xp(8)
            if xp_msg:
                msgs.append((xp_msg, C["amber2"]))

            for msg, col in msgs:
                _log_add_render(msg, col)

            update_stats()
            rebuild_actions()

            # ── Verificar fin ──
            if not enemigo.esta_vivo():
                self.after(400, lambda: self._victoria_batalla())
                return
            if not hero.esta_vivo():
                self.after(400, lambda: self._show_gameover())
                return

        rebuild_actions()

    def _render_log(self):
        for w in self._log_inner.winfo_children():
            w.destroy()
        # Mostrar últimas 30 entradas
        for msg, color in self.state.log[-30:]:
            tk.Label(self._log_inner, text=msg,
                     bg=C["bg2"], fg=color,
                     font=FONTS["mono_sm"], anchor="w",
                     justify="left", wraplength=700).pack(
                         fill=tk.X, padx=8, pady=0)
        # Auto-scroll al final
        aid = self.after(50, lambda: self._log_canvas_ref.yview_moveto(1.0))
        self._anim_ids.append(aid)

    # ── VICTORIA DE BATALLA ─────────────────────────────────────────────
    def _victoria_batalla(self):
        self._clear_content()
        hero    = self.state.hero
        enemigo = self.state.enemigo
        nd      = self.state.nivel_actual

        xp_bonus   = enemigo.xp_recompensa
        oro_bonus  = enemigo.oro_recompensa
        xp_msg     = hero.ganar_xp(xp_bonus)
        hero.oro  += oro_bonus
        self.state.puntaje += xp_bonus * 2
        self._lbl_puntaje.config(text=f"⭐ {self.state.puntaje} pts")

        hero.aprender_concepto(nd.concepto)

        f = tk.Frame(self.content, bg=C["bg"])
        f.pack(expand=True)

        tk.Label(f, text="🎉", bg=C["bg"], font=FONTS["emoji"]).pack(pady=(30,4))
        tk.Label(f, text="¡ENEMIGO DERROTADO!",
                 bg=C["bg"], fg=C["green"], font=FONTS["h1"]).pack()
        tk.Label(f, text=f"Has derrotado a {enemigo.nombre}",
                 bg=C["bg"], fg=C["gray"], font=FONTS["lg"]).pack(pady=4)

        # Recompensas
        rew_f = tk.Frame(f, bg=C["bg3"], padx=20, pady=14)
        rew_f.pack(padx=40, pady=12, fill=tk.X)
        tk.Label(rew_f, text="RECOMPENSAS", bg=C["bg3"],
                 fg=C["amber"], font=FONTS["h3"]).pack()
        for txt, col in [
            (f"⭐ +{xp_bonus} XP", C["xp_bar"]),
            (f"💰 +{oro_bonus} Oro", C["amber2"]),
            (xp_msg or "", C["amber2"]),
            (f"📚 Concepto aprendido: {nd.concepto}", nd.color),
        ]:
            if txt.strip():
                tk.Label(rew_f, text=txt, bg=C["bg3"],
                         fg=col, font=FONTS["body"]).pack(pady=1)

        # Conceptos aprendidos
        tk.Frame(f, bg=C["border"], height=1, width=400).pack(pady=12)
        aprendidos = hero.conceptos_aprendidos
        ck_f = tk.Frame(f, bg=C["bg"])
        ck_f.pack()
        todos = ["Clases y Objetos", "Métodos", "Herencia",
                 "Encapsulamiento", "Polimorfismo", "Abstracción"]
        for i, c in enumerate(todos):
            ok    = c in aprendidos
            color = C["green"] if ok else C["dim"]
            emoji = "✅" if ok else "⬜"
            tk.Label(ck_f, text=f"{emoji} {c}",
                     bg=C["bg"], fg=color,
                     font=FONTS["sm"]).grid(row=i//3, column=i%3, padx=8, pady=2, sticky="w")

        self._make_button(f, "📝  Continuar al Quiz",
                          self._show_quiz, C["amber"]).pack(pady=16)

    # ── QUIZ ────────────────────────────────────────────────────────────
    def _show_quiz(self):
        self._clear_content()
        nd   = self.state.nivel_actual
        hero = self.state.hero

        f = tk.Frame(self.content, bg=C["bg"])
        f.pack(expand=True, padx=40, pady=20)

        badge = tk.Label(f,
                          text=f"  {nd.emoji_concepto}  QUIZ — {nd.concepto}  ",
                          bg=nd.color, fg=C["bg"], font=FONTS["h3"])
        badge.pack(pady=(0,12))

        tk.Label(f, text=nd.quiz_pregunta,
                 bg=C["bg"], fg=C["white"],
                 font=FONTS["h2"], wraplength=700).pack(pady=(0,16))

        selected = tk.IntVar(value=-1)
        self._quiz_buttons = []
        self._quiz_answered = False

        result_lbl = tk.Label(f, text="", bg=C["bg"],
                               font=FONTS["h3"], wraplength=700)
        tip_lbl    = tk.Label(f, text="", bg=C["bg"],
                               fg=C["cyan"], font=FONTS["body"],
                               wraplength=700, justify="left")

        next_btn = self._make_button(f, "Siguiente nivel →",
                                      self._siguiente_nivel, C["amber"])

        def elegir(idx: int):
            if self._quiz_answered:
                return
            self._quiz_answered = True
            correcta = nd.quiz_correcta

            for i, (btn_w, _) in enumerate(self._quiz_buttons):
                if i == correcta:
                    btn_w.config(bg=C["green"], fg=C["bg"])
                elif i == idx:
                    btn_w.config(bg=C["red"], fg=C["white"])

            if idx == correcta:
                self.state.racha_correctas += 1
                bonus = 50 * self.state.racha_correctas
                self.state.puntaje += bonus
                xp_msg = hero.ganar_xp(50)
                result_lbl.config(
                    text=f"✅ ¡CORRECTO! +{bonus} puntos (racha ×{self.state.racha_correctas})",
                    fg=C["green"])
            else:
                self.state.racha_correctas = 0
                result_lbl.config(
                    text=f"❌ Incorrecto. La respuesta correcta era la opción {correcta+1}.",
                    fg=C["red"])

            tip_lbl.config(text=nd.quiz_tip)
            self._lbl_puntaje.config(text=f"⭐ {self.state.puntaje} pts")
            next_btn.pack(pady=12)

        # Opciones
        for i, opcion in enumerate(nd.quiz_opciones):
            texto = f"{chr(65+i)})  {opcion}"
            b = self._make_button(f, texto,
                                  lambda idx=i: elegir(idx),
                                  C["bg3"], C["white"],
                                  font=FONTS["body"])
            b.pack(fill=tk.X, pady=3)
            self._quiz_buttons.append((b, i))

        result_lbl.pack(pady=8)
        tip_lbl.pack(pady=4)
        # next_btn se empaqueta dentro de elegir()

    # ── SIGUIENTE NIVEL / FIN ───────────────────────────────────────────
    def _siguiente_nivel(self):
        if self.state.es_ultimo_nivel():
            self._show_fin_juego()
        else:
            self.state.nivel_idx += 1
            self._cargar_nivel()

    # ── FIN DE JUEGO ────────────────────────────────────────────────────
    def _show_fin_juego(self):
        self._clear_content()
        hero    = self.state.hero
        elapsed = int(time.time() - self.state.tiempo_inicio)
        mins, secs = divmod(elapsed, 60)

        self._lbl_nivel_top.config(text="🏆 ¡JUEGO COMPLETADO!")
        self._lbl_puntaje.config(text=f"⭐ {self.state.puntaje} pts FINAL")

        f = tk.Frame(self.content, bg=C["bg"])
        f.pack(expand=True)

        tk.Label(f, text="🏆", bg=C["bg"], font=FONTS["emoji"]).pack(pady=(20,4))
        tk.Label(f, text="¡HAS COMPLETADO OOP QUEST!",
                 bg=C["bg"], fg=C["amber"], font=FONTS["title"]).pack()
        tk.Label(f, text="¡Dominas los 4 pilares de la POO!",
                 bg=C["bg"], fg=C["green"], font=FONTS["h2"]).pack(pady=4)

        # Certificado
        cert_f = tk.Frame(f, bg=C["bg2"], padx=24, pady=18,
                          highlightthickness=2, highlightbackground=C["amber"])
        cert_f.pack(padx=30, pady=12)

        tk.Label(cert_f, text="🎓 CERTIFICADO DE COMPLETACIÓN",
                 bg=C["bg2"], fg=C["amber"], font=FONTS["h2"]).pack()
        tk.Frame(cert_f, bg=C["amber"], height=1).pack(fill=tk.X, pady=8)

        for txt, col in [
            (f"{hero.emoji} Héroe: {hero.nombre} [{hero.clase}] Nivel {hero.nivel}", C["white"]),
            (f"⭐ Puntaje final: {self.state.puntaje} puntos", C["amber2"]),
            (f"⏱️ Tiempo: {mins:02d}:{secs:02d}", C["gray"]),
        ]:
            tk.Label(cert_f, text=txt, bg=C["bg2"], fg=col,
                     font=FONTS["body"]).pack(pady=2)

        tk.Frame(cert_f, bg=C["border"], height=1).pack(fill=tk.X, pady=8)

        tk.Label(cert_f, text="Conceptos dominados:",
                 bg=C["bg2"], fg=C["gray"], font=FONTS["sm"]).pack()
        conceptos_f = tk.Frame(cert_f, bg=C["bg2"])
        conceptos_f.pack()
        for c in ["Clases y Objetos", "Métodos", "Herencia",
                  "Encapsulamiento", "Polimorfismo", "Abstracción"]:
            tk.Label(conceptos_f, text=f"✅ {c}",
                     bg=C["bg2"], fg=C["green"],
                     font=FONTS["body"]).pack(anchor="w")

        # Récord
        self._guardar_puntaje()
        mejores = self._cargar_puntajes()
        if mejores:
            tk.Frame(cert_f, bg=C["border"], height=1).pack(fill=tk.X, pady=8)
            tk.Label(cert_f, text="🏅 TOP PUNTAJES",
                     bg=C["bg2"], fg=C["amber"], font=FONTS["sm"]).pack()
            for i, (n, p, t) in enumerate(mejores[:3], 1):
                tk.Label(cert_f, text=f"{i}. {n}: {p}pts en {t}",
                         bg=C["bg2"], fg=C["gray"], font=FONTS["sm"]).pack()

        btns_f = tk.Frame(f, bg=C["bg"])
        btns_f.pack(pady=12)
        self._make_button(btns_f, "▶ JUGAR DE NUEVO", self._show_menu,
                          C["amber"]).pack(side=tk.LEFT, padx=8)

    def _show_gameover(self):
        self._clear_content()
        f = tk.Frame(self.content, bg=C["bg"])
        f.pack(expand=True)

        tk.Label(f, text="💀", bg=C["bg"], font=FONTS["emoji"]).pack(pady=(30,4))
        tk.Label(f, text="GAME OVER",
                 bg=C["bg"], fg=C["red"], font=FONTS["title"]).pack()
        tk.Label(f, text=f"{self.state.hero.nombre} ha caído en combate...",
                 bg=C["bg"], fg=C["gray"], font=FONTS["lg"]).pack(pady=6)
        tk.Label(f, text=f"Puntaje: {self.state.puntaje} pts | Nivel alcanzado: {self.state.nivel_idx+1}",
                 bg=C["bg"], fg=C["amber"], font=FONTS["body"]).pack(pady=4)

        tk.Label(f,
                 text="💡 Consejo: Lee bien la lección antes de entrar a la batalla.\n"
                      "Los hechizos de buff y cura son cruciales para sobrevivir.",
                 bg=C["bg"], fg=C["cyan"], font=FONTS["body"], wraplength=500).pack(pady=12)

        self._make_button(f, "▶ INTENTAR DE NUEVO", self._show_menu,
                          C["amber"]).pack(pady=6)

    # ── PERSISTENCIA ────────────────────────────────────────────────────
    def _guardar_puntaje(self):
        try:
            ruta  = Path(__file__).parent / "oopquest_scores.json"
            datos = self._cargar_puntajes()
            elapsed = int(time.time() - self.state.tiempo_inicio)
            mins, secs = divmod(elapsed, 60)
            nuevo = [self.state.hero.nombre,
                     self.state.puntaje,
                     f"{mins:02d}:{secs:02d}"]
            datos.append(nuevo)
            datos.sort(key=lambda x: x[1], reverse=True)
            with open(ruta, "w") as fp:
                json.dump(datos[:10], fp)
        except Exception:
            pass

    @staticmethod
    def _cargar_puntajes() -> list:
        try:
            ruta = Path(__file__).parent / "oopquest_scores.json"
            if ruta.exists():
                with open(ruta) as fp:
                    return json.load(fp)
        except Exception:
            pass
        return []


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = OOPQuestApp()
    app.mainloop()
