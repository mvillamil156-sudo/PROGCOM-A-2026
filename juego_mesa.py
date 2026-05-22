# Clase principal
class JuegoMesa:
    def __init__(self, nombre, jugadores):
        self.nombre = nombre
        self.jugadores = jugadores
        self.turno = 1

    def mostrar_info(self):
        print(f"Juego: {self.nombre}")
        print(f"Jugadores: {self.jugadores}")
        print(f"Turno: {self.turno}")

    def siguiente_turno(self):
        self.turno += 1
        print(f"¡Turno {self.turno}!")


# Usar el objeto
mi_juego = JuegoMesa("Catan", 4)
mi_juego.mostrar_info()
mi_juego.siguiente_turno()
