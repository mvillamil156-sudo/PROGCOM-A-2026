import tkinter as tk
from tkinter import ttk

errores = [
    # ── PYTHON ────────────────────────────────────────────────────────────────
    {
        "num": "01", "lenguaje": "Python",
        "nombre": "KeyError — Clave inexistente en diccionario",
        "descripcion": "Ocurre cuando intentas acceder a una clave que no existe en el diccionario. Python lanza un error en lugar de retornar vacío.",
        "error": 'paises = {"U.S.A": 156, "China": 2356, "Germany": 897}\n\nprint(paises["Japan"])   # KeyError: \'Japan\'',
        "solucion": 'paises = {"U.S.A": 156, "China": 2356, "Germany": 897}\n\n# Usar .get() → retorna None si no existe\nprint(paises.get("Japan", "No encontrado"))\n\n# O verificar antes\nif "Japan" in paises:\n    print(paises["Japan"])\nelse:\n    print("Clave no encontrada")',
        "tip": 'Usa siempre .get() cuando no estes seguro de que la clave existe.',
    },
    {
        "num": "02", "lenguaje": "Python",
        "nombre": "IndexError — Indice fuera del rango",
        "descripcion": "Ocurre al intentar acceder a una posicion que no existe en una lista. Si la lista tiene 3 elementos, el ultimo indice valido es 2, no 3.",
        "error": "notas = [8.5, 9.0, 7.3]   # indices: 0, 1, 2\n\nprint(notas[5])            # IndexError: list index out of range",
        "solucion": "notas = [8.5, 9.0, 7.3]\n\nindice = 5\nif indice < len(notas):\n    print(notas[indice])\nelse:\n    print(f\"Indice invalido. La lista tiene {len(notas)} elementos.\")",
        "tip": "El ultimo indice valido siempre es len(lista) - 1.",
    },
    {
        "num": "03", "lenguaje": "Python",
        "nombre": "TypeError — Mezclar texto con numero",
        "descripcion": "input() siempre devuelve texto (str). Si intentas sumarle un numero sin convertirlo primero, Python lanza un TypeError.",
        "error": 'edad = input("Tu edad: ")   # retorna str, ej: "17"\n\nresultado = edad + 5        # TypeError: can only concatenate str to str',
        "solucion": 'edad = int(input("Tu edad: "))   # convertir a entero\n\nresultado = edad + 5\nprint(f"En 5 anos tendras {resultado} anos")',
        "tip": "Siempre convierte con int() o float() lo que leas con input().",
    },
    {
        "num": "04", "lenguaje": "Python",
        "nombre": "ZeroDivisionError — Division entre cero",
        "descripcion": "Dividir cualquier numero entre 0 es matematicamente imposible. Python detiene el programa si ocurre sin manejo.",
        "error": "total = 100\ncantidad = 0\n\npromedio = total / cantidad   # ZeroDivisionError: division by zero",
        "solucion": "total = 100\ncantidad = 0\n\nif cantidad != 0:\n    promedio = total / cantidad\n    print(f\"Promedio: {promedio}\")\nelse:\n    print(\"No se puede dividir entre cero\")",
        "tip": "Valida que el divisor sea distinto de 0 antes de operar.",
    },
    {
        "num": "05", "lenguaje": "Python",
        "nombre": "NameError — Variable usada antes de crearla",
        "descripcion": "Ocurre al usar una variable que no has definido, o que escribiste con otro nombre. Python distingue MAYUSCULAS de minusculas.",
        "error": "print(nombre)        # NameError: name 'nombre' is not defined\n\n# Tambien pasa por typo:\nNombre = \"Juan\"\nprint(nombre)        # NameError: Nombre != nombre",
        "solucion": "nombre = \"Juan\"      # definir ANTES de usar\nprint(nombre)        # Juan\n\n# Cuidar mayusculas\nnombre = \"Maria\"\nprint(nombre)        # Maria",
        "tip": "Declara tus variables antes de usarlas. Python es case-sensitive.",
    },
    {
        "num": "06", "lenguaje": "Python",
        "nombre": "AttributeError — Metodo inexistente en el tipo",
        "descripcion": "Ocurre cuando llamas un metodo que no pertenece al tipo del objeto. Por ejemplo, llamar .upper() sobre un entero.",
        "error": 'numero = 42\nresultado = numero.upper()   # AttributeError: \'int\' object has no attribute \'upper\'',
        "solucion": 'numero = 42\n\n# Convertir a texto primero si se necesita\nresultado = str(numero).upper()\nprint(resultado)   # "42"',
        "tip": "Verifica el tipo del objeto con type() antes de llamar metodos especificos de cadenas.",
    },
    {
        "num": "07", "lenguaje": "Python",
        "nombre": "ValueError — Conversion de tipo invalida",
        "descripcion": "Ocurre al intentar convertir un texto que no representa un numero valido con int() o float().",
        "error": 'texto = "hola"\nnumero = int(texto)   # ValueError: invalid literal for int() with base 10',
        "solucion": 'texto = "hola"\n\ntry:\n    numero = int(texto)\nexcept ValueError:\n    print(f"No se puede convertir \'{texto}\' a entero")',
        "tip": "Usa try/except al convertir entradas del usuario. Nunca asumas el formato.",
    },
    {
        "num": "08", "lenguaje": "Python",
        "nombre": "FileNotFoundError — Archivo inexistente",
        "descripcion": "Ocurre al intentar abrir un archivo que no existe en la ruta indicada. Muy comun con rutas relativas incorrectas.",
        "error": 'with open("datos.txt", "r") as f:   # FileNotFoundError\n    contenido = f.read()',
        "solucion": 'import os\n\nruta = "datos.txt"\nif os.path.exists(ruta):\n    with open(ruta, "r") as f:\n        contenido = f.read()\nelse:\n    print(f"Archivo no encontrado: {ruta}")',
        "tip": "Usa os.path.exists() antes de abrir archivos, o maneja el error con try/except.",
    },
    {
        "num": "09", "lenguaje": "Python",
        "nombre": "RecursionError — Recursion infinita",
        "descripcion": "Python limita la profundidad de recursion (~1000 llamadas). Si una funcion recursiva no tiene caso base, se lanza este error.",
        "error": "def factorial(n):\n    return n * factorial(n - 1)   # sin caso base -> RecursionError\n\nprint(factorial(5))",
        "solucion": "def factorial(n):\n    if n == 0 or n == 1:   # caso base\n        return 1\n    return n * factorial(n - 1)\n\nprint(factorial(5))   # 120",
        "tip": "Toda funcion recursiva necesita un caso base claro que detenga la recursion.",
    },
    {
        "num": "10", "lenguaje": "Python",
        "nombre": "IndentationError — Sangria incorrecta",
        "descripcion": "Python usa la sangria (espacios o tabulaciones) para definir bloques. Mezclar ambos o no ser consistente causa este error.",
        "error": "def saludar():\n    print(\"Hola\")\n  print(\"Mundo\")   # IndentationError: unexpected indent",
        "solucion": "def saludar():\n    print(\"Hola\")\n    print(\"Mundo\")   # misma sangria: 4 espacios\n\nsaludar()",
        "tip": "Usa siempre 4 espacios por nivel de sangria. Nunca mezcles tabs y espacios.",
    },
    {
        "num": "11", "lenguaje": "Python",
        "nombre": "SyntaxError — Error de sintaxis",
        "descripcion": "Python no puede leer tu codigo porque falta algun elemento de la sintaxis: parentesis, dos puntos, comillas, etc.",
        "error": "if x > 5\n    print(\"Mayor\")   # SyntaxError: expected ':'",
        "solucion": "if x > 5:\n    print(\"Mayor\")\nelse:\n    print(\"Menor o igual\")",
        "tip": "Lee el mensaje del error: Python indica la linea y el caracter donde detecto el problema.",
    },
    {
        "num": "12", "lenguaje": "Python",
        "nombre": "ImportError — Modulo no instalado",
        "descripcion": "Ocurre al intentar importar un modulo que no esta instalado en el entorno actual.",
        "error": "import pandas as pd   # ImportError: No module named 'pandas'\n\ndf = pd.read_csv(\"datos.csv\")",
        "solucion": "# Primero instalar en la terminal:\n# pip install pandas\n\nimport pandas as pd\ndf = pd.read_csv(\"datos.csv\")\nprint(df.head())",
        "tip": "Si el modulo es externo, instalalo con pip. Si es propio, verifica la ruta.",
    },
    {
        "num": "13", "lenguaje": "Python",
        "nombre": "StopIteration — Iterador agotado",
        "descripcion": "Ocurre al llamar next() sobre un iterador que ya no tiene mas elementos.",
        "error": "nums = iter([1, 2])\nnext(nums)   # 1\nnext(nums)   # 2\nnext(nums)   # StopIteration",
        "solucion": "nums = iter([1, 2])\n\n# Usar next() con valor por defecto\nval = next(nums, \"fin\")\nprint(val)   # 1\nval = next(nums, \"fin\")\nprint(val)   # 2\nval = next(nums, \"fin\")\nprint(val)   # fin (sin error)",
        "tip": "Pasa un segundo argumento a next() como valor por defecto para evitar la excepcion.",
    },
    {
        "num": "14", "lenguaje": "Python",
        "nombre": "OverflowError — Numero demasiado grande para float",
        "descripcion": "Ocurre cuando el resultado de un calculo matematico excede el limite de representacion de float en Python.",
        "error": "import math\nresultado = math.exp(1000)   # OverflowError: math range error",
        "solucion": "import math\n\ntry:\n    resultado = math.exp(1000)\nexcept OverflowError:\n    print(\"El numero es demasiado grande para float\")\n    # Usar decimal para mayor precision\n    from decimal import Decimal\n    resultado = Decimal(1000).exp()",
        "tip": "Usa el modulo decimal cuando necesites operar con numeros muy grandes con precision.",
    },
    {
        "num": "15", "lenguaje": "Python",
        "nombre": "UnboundLocalError — Variable local no asignada",
        "descripcion": "Ocurre cuando una funcion usa una variable antes de asignarle un valor local, aunque exista una global con el mismo nombre.",
        "error": "contador = 10\n\ndef incrementar():\n    contador += 1   # UnboundLocalError\n    print(contador)\n\nincrementar()",
        "solucion": "contador = 10\n\ndef incrementar():\n    global contador   # declarar que se usa la global\n    contador += 1\n    print(contador)\n\nincrementar()   # 11",
        "tip": "Usa 'global' para modificar variables globales dentro de funciones, o pasa la variable como parametro.",
    },
    {
        "num": "16", "lenguaje": "Python",
        "nombre": "MemoryError — Sin memoria suficiente",
        "descripcion": "Python intenta reservar mas RAM de la disponible. Suele ocurrir al crear listas u objetos enormes innecesariamente.",
        "error": "# Crear una lista de 100 millones de elementos\nlista = [0] * 100_000_000_000   # MemoryError",
        "solucion": "# Usar generadores en lugar de listas grandes\ndef generar_ceros(n):\n    for _ in range(n):\n        yield 0\n\ngenerador = generar_ceros(100_000_000_000)\nprint(next(generador))   # 0 (sin cargar todo en memoria)",
        "tip": "Usa generadores (yield) cuando no necesites todos los datos a la vez en memoria.",
    },
    {
        "num": "17", "lenguaje": "Python",
        "nombre": "TypeError — Objeto no iterable",
        "descripcion": "Ocurre al intentar iterar sobre un tipo que no es iterable, como un entero o None.",
        "error": "numero = 42\nfor x in numero:   # TypeError: 'int' object is not iterable\n    print(x)",
        "solucion": "# Si quieres iterar un rango\nfor x in range(42):\n    print(x)\n\n# Si es una lista de un elemento\nfor x in [42]:\n    print(x)",
        "tip": "Verifica que el objeto sea lista, tupla, string u otro iterable antes de usar un for.",
    },
    {
        "num": "18", "lenguaje": "Python",
        "nombre": "AssertionError — Condicion de asercion fallida",
        "descripcion": "Ocurre cuando una sentencia assert evalua a False. Se usa para validar suposiciones durante el desarrollo.",
        "error": "def dividir(a, b):\n    assert b != 0, \"El divisor no puede ser cero\"\n    return a / b\n\nresultado = dividir(10, 0)   # AssertionError: El divisor no puede ser cero",
        "solucion": "def dividir(a, b):\n    if b == 0:\n        raise ValueError(\"El divisor no puede ser cero\")\n    return a / b\n\ntry:\n    print(dividir(10, 2))   # 5.0\n    print(dividir(10, 0))\nexcept ValueError as e:\n    print(e)",
        "tip": "assert es para pruebas internas; usa raise con excepciones propias para validaciones de produccion.",
    },
    {
        "num": "19", "lenguaje": "Python",
        "nombre": "OSError — Error al operar con el sistema de archivos",
        "descripcion": "Ocurre al intentar crear, renombrar o eliminar archivos en directorios sin permisos o inexistentes.",
        "error": "import os\nos.mkdir(\"/ruta/que/no/existe/carpeta\")   # FileNotFoundError (subclase de OSError)",
        "solucion": "import os\n\nruta = \"/ruta/nueva/carpeta\"\ntry:\n    os.makedirs(ruta, exist_ok=True)   # crea toda la cadena de directorios\n    print(\"Directorio creado\")\nexcept PermissionError:\n    print(\"Sin permisos para crear el directorio\")",
        "tip": "Usa os.makedirs(ruta, exist_ok=True) para crear directorios anidados sin errores si ya existen.",
    },
    {
        "num": "20", "lenguaje": "Python",
        "nombre": "RuntimeError — Cambio de tamano de lista durante iteracion",
        "descripcion": "Modificar una lista (agregar o eliminar elementos) mientras la iteras puede causar comportamientos inesperados o excepciones.",
        "error": "numeros = [1, 2, 3, 4, 5]\n\nfor n in numeros:\n    if n % 2 == 0:\n        numeros.remove(n)   # RuntimeError o resultados incorrectos",
        "solucion": "numeros = [1, 2, 3, 4, 5]\n\n# Iterar sobre una copia\nnumeros = [n for n in numeros if n % 2 != 0]\nprint(numeros)   # [1, 3, 5]",
        "tip": "Nunca modifiques una lista mientras la iteras. Crea una nueva lista con comprension.",
    },
    {
        "num": "21", "lenguaje": "Python",
        "nombre": "UnicodeDecodeError — Error de codificacion al leer archivo",
        "descripcion": "Ocurre cuando Python intenta decodificar bytes con una codificacion incorrecta, frecuente al leer archivos con tildes o caracteres especiales.",
        "error": "with open(\"datos.txt\", \"r\") as f:   # usa utf-8 por defecto\n    texto = f.read()               # UnicodeDecodeError si el archivo es latin-1",
        "solucion": "# Especificar la codificacion correcta\nwith open(\"datos.txt\", \"r\", encoding=\"latin-1\") as f:\n    texto = f.read()\n\n# O ignorar caracteres problematicos\nwith open(\"datos.txt\", \"r\", encoding=\"utf-8\", errors=\"ignore\") as f:\n    texto = f.read()",
        "tip": "Especifica siempre encoding='utf-8' (o el correcto) al abrir archivos de texto.",
    },
    {
        "num": "22", "lenguaje": "Python",
        "nombre": "PermissionError — Sin permisos de escritura",
        "descripcion": "El sistema operativo impide la operacion porque el proceso no tiene los permisos necesarios sobre el archivo o directorio.",
        "error": "with open(\"/etc/hosts\", \"w\") as f:   # PermissionError: [Errno 13]\n    f.write(\"127.0.0.1 mi-sitio\")",
        "solucion": "import os\n\nruta = \"/etc/hosts\"\ntry:\n    with open(ruta, \"w\") as f:\n        f.write(\"127.0.0.1 mi-sitio\")\nexcept PermissionError:\n    print(f\"Sin permisos para escribir en {ruta}. Ejecuta como administrador.\")",
        "tip": "Escribe siempre en directorios donde el usuario tiene permisos, como la carpeta del proyecto.",
    },
    {
        "num": "23", "lenguaje": "Python",
        "nombre": "TimeoutError — Operacion de red excede el tiempo limite",
        "descripcion": "Ocurre en operaciones de red o I/O cuando el recurso remoto no responde dentro del tiempo configurado.",
        "error": "import urllib.request\n\nrespuesta = urllib.request.urlopen(\"https://ejemplo.com\")   # TimeoutError si no responde",
        "solucion": "import urllib.request\n\ntry:\n    respuesta = urllib.request.urlopen(\"https://ejemplo.com\", timeout=5)\n    print(respuesta.read())\nexcept TimeoutError:\n    print(\"El servidor no respondio en el tiempo esperado\")",
        "tip": "Configura siempre un timeout en operaciones de red para evitar bloqueos indefinidos.",
    },
    {
        "num": "24", "lenguaje": "Python",
        "nombre": "NotImplementedError — Metodo abstracto sin implementar",
        "descripcion": "Se lanza cuando un metodo declarado en una clase base no ha sido implementado en la subclase.",
        "error": "class Animal:\n    def hablar(self):\n        raise NotImplementedError(\"Debes implementar hablar()\")\n\nclass Perro(Animal):\n    pass\n\np = Perro()\np.hablar()   # NotImplementedError",
        "solucion": "class Animal:\n    def hablar(self):\n        raise NotImplementedError(\"Debes implementar hablar()\")\n\nclass Perro(Animal):\n    def hablar(self):   # implementacion requerida\n        return \"Guau!\"\n\np = Perro()\nprint(p.hablar())   # Guau!",
        "tip": "Si heredas de una clase base con NotImplementedError, debes sobrescribir el metodo en la subclase.",
    },
    {
        "num": "25", "lenguaje": "Python",
        "nombre": "EOFError — Fin de archivo inesperado en input()",
        "descripcion": "Ocurre cuando input() intenta leer datos pero no hay nada mas que leer (por ejemplo, en scripts automatizados o stdin redirigido).",
        "error": "# Al ejecutar: echo '' | python script.py\nnombre = input(\"Ingresa tu nombre: \")   # EOFError: EOF when reading a line",
        "solucion": "try:\n    nombre = input(\"Ingresa tu nombre: \")\n    print(f\"Hola, {nombre}\")\nexcept EOFError:\n    print(\"No se recibio entrada. Usando valor por defecto.\")\n    nombre = \"Usuario\"",
        "tip": "Maneja EOFError cuando tu script puede recibir entrada de archivos o pipelines en lugar del teclado.",
    },
    {
        "num": "26", "lenguaje": "Python",
        "nombre": "ConnectionError — Fallo de conexion de red",
        "descripcion": "Ocurre cuando una solicitud de red no puede establecer conexion con el servidor de destino.",
        "error": "import requests\n\nrespuesta = requests.get(\"https://servidor-que-no-existe.xyz\")   # ConnectionError",
        "solucion": "import requests\n\ntry:\n    respuesta = requests.get(\"https://servidor-que-no-existe.xyz\", timeout=5)\n    respuesta.raise_for_status()\n    print(respuesta.json())\nexcept requests.exceptions.ConnectionError:\n    print(\"No se pudo conectar. Verifica tu conexion a internet.\")\nexcept requests.exceptions.Timeout:\n    print(\"La solicitud tardo demasiado.\")",
        "tip": "Siempre envuelve llamadas HTTP en try/except y configura un timeout.",
    },
    {
        "num": "27", "lenguaje": "Python",
        "nombre": "TypeError — Argumento de tipo incorrecto en funcion",
        "descripcion": "Ocurre cuando pasas un argumento de tipo distinto al esperado por una funcion que no acepta ese tipo.",
        "error": "def sumar(a, b):\n    return a + b\n\nresultado = sumar(\"3\", 5)   # TypeError: can only concatenate str (not int) to str",
        "solucion": "def sumar(a, b):\n    return float(a) + float(b)   # convertir antes de operar\n\nresultado = sumar(\"3\", 5)\nprint(resultado)   # 8.0",
        "tip": "Convierte los tipos al inicio de la funcion o usa anotaciones de tipo para documentar lo esperado.",
    },
    {
        "num": "28", "lenguaje": "Python",
        "nombre": "KeyboardInterrupt — El usuario interrumpe la ejecucion",
        "descripcion": "Ocurre cuando el usuario presiona Ctrl+C para interrumpir el programa. Si no se maneja, el programa termina abruptamente.",
        "error": "while True:\n    dato = input(\"Ingresa un numero: \")\n    print(int(dato) * 2)\n# Ctrl+C -> KeyboardInterrupt: imprime traza de error fea",
        "solucion": "print(\"Presiona Ctrl+C para salir\")\ntry:\n    while True:\n        dato = input(\"Ingresa un numero: \")\n        print(int(dato) * 2)\nexcept KeyboardInterrupt:\n    print(\"\\nPrograma terminado por el usuario. ¡Hasta luego!\")",
        "tip": "Captura KeyboardInterrupt para cerrar recursos y mostrar un mensaje amigable al usuario.",
    },
    {
        "num": "29", "lenguaje": "Python",
        "nombre": "IsADirectoryError — Se intenta leer un directorio como archivo",
        "descripcion": "Ocurre cuando open() recibe la ruta de un directorio en lugar de un archivo.",
        "error": "with open(\"/home/usuario/documentos\", \"r\") as f:   # IsADirectoryError\n    contenido = f.read()",
        "solucion": "import os\n\nruta = \"/home/usuario/documentos\"\n\nif os.path.isfile(ruta):\n    with open(ruta, \"r\") as f:\n        contenido = f.read()\nelif os.path.isdir(ruta):\n    print(\"La ruta es un directorio, no un archivo\")\n    print(os.listdir(ruta))",
        "tip": "Usa os.path.isfile() para verificar que la ruta apunta a un archivo antes de abrirlo.",
    },
    {
        "num": "30", "lenguaje": "Python",
        "nombre": "FloatingPointError — Imprecision en aritmetica flotante",
        "descripcion": "Los numeros de punto flotante tienen precision limitada en binario, generando resultados inesperados en comparaciones o sumas.",
        "error": "resultado = 0.1 + 0.2\nprint(resultado)        # 0.30000000000000004\nprint(resultado == 0.3) # False  ← error logico",
        "solucion": "import math\n\nresultado = 0.1 + 0.2\n\n# Comparar con tolerancia\nprint(math.isclose(resultado, 0.3))   # True\n\n# O usar round para mostrar\nprint(round(resultado, 2))            # 0.3\n\n# Para finanzas, usar decimal\nfrom decimal import Decimal\nprint(Decimal(\"0.1\") + Decimal(\"0.2\"))  # 0.3",
        "tip": "Nunca compares floats con ==. Usa math.isclose() o redondea antes de comparar.",
    },

    # ── JAVA ──────────────────────────────────────────────────────────────────
    {
        "num": "31", "lenguaje": "Java",
        "nombre": "NullPointerException — Objeto no inicializado",
        "descripcion": "El error mas comun en Java. Ocurre cuando intentas usar un metodo o atributo de un objeto que vale null (no fue inicializado).",
        "error": "public class Ejemplo {\n    public static void main(String[] args) {\n        String nombre = null;\n        System.out.println(nombre.length());  // NullPointerException\n    }\n}",
        "solucion": "public class Ejemplo {\n    public static void main(String[] args) {\n        String nombre = null;\n\n        if (nombre != null) {\n            System.out.println(nombre.length());\n        } else {\n            System.out.println(\"El nombre esta vacio\");\n        }\n    }\n}",
        "tip": "Siempre inicializa tus objetos. Verifica != null antes de usarlos.",
    },
    {
        "num": "32", "lenguaje": "Java",
        "nombre": "ArrayIndexOutOfBoundsException — Indice invalido",
        "descripcion": "Ocurre al acceder a un indice que no existe en el arreglo. Equivalente al IndexError de Python, pero en Java.",
        "error": "public class Main {\n    public static void main(String[] args) {\n        int[] notas = {85, 90, 73};         // longitud = 3\n        System.out.println(notas[5]);        // ArrayIndexOutOfBoundsException\n    }\n}",
        "solucion": "public class Main {\n    public static void main(String[] args) {\n        int[] notas = {85, 90, 73};\n        int indice = 5;\n\n        if (indice >= 0 && indice < notas.length) {\n            System.out.println(notas[indice]);\n        } else {\n            System.out.println(\"Indice invalido. Tamano: \" + notas.length);\n        }\n    }\n}",
        "tip": "Valida el indice con notas.length antes de acceder al arreglo.",
    },
    {
        "num": "33", "lenguaje": "Java",
        "nombre": "NumberFormatException — Texto no numerico a numero",
        "descripcion": "Ocurre al intentar convertir un String a numero cuando el texto no representa un valor numerico valido.",
        "error": "public class Main {\n    public static void main(String[] args) {\n        String valor = \"hola\";\n        int numero = Integer.parseInt(valor);  // NumberFormatException\n    }\n}",
        "solucion": "public class Main {\n    public static void main(String[] args) {\n        String valor = \"hola\";\n\n        try {\n            int numero = Integer.parseInt(valor);\n            System.out.println(numero);\n        } catch (NumberFormatException e) {\n            System.out.println(\"Valor no valido: \" + valor);\n        }\n    }\n}",
        "tip": "Usa try/catch al convertir texto a numero. Nunca asumas que el String es numerico.",
    },
    {
        "num": "34", "lenguaje": "Java",
        "nombre": "StackOverflowError — Recursion infinita",
        "descripcion": "Ocurre cuando una funcion se llama a si misma sin condicion de parada, llenando la pila de llamadas.",
        "error": "public class Main {\n    static void contar(int n) {\n        System.out.println(n);\n        contar(n + 1);   // nunca para -> StackOverflowError\n    }\n\n    public static void main(String[] args) {\n        contar(1);\n    }\n}",
        "solucion": "public class Main {\n    static void contar(int n) {\n        if (n > 10) return;   // condicion de parada\n        System.out.println(n);\n        contar(n + 1);\n    }\n\n    public static void main(String[] args) {\n        contar(1);   // imprime del 1 al 10\n    }\n}",
        "tip": "Toda funcion recursiva DEBE tener un caso base que detenga la recursion.",
    },
    {
        "num": "35", "lenguaje": "Java",
        "nombre": "ClassCastException — Conversion de tipo incorrecta",
        "descripcion": "Ocurre al hacer un cast explicito incorrecto. El objeto no pertenece a la clase a la que intentas convertirlo.",
        "error": "Object obj = \"Hola mundo\";            // es un String\n\nInteger num = (Integer) obj;          // ClassCastException\nSystem.out.println(num);",
        "solucion": "Object obj = \"Hola mundo\";\n\n// Verificar tipo con instanceof antes del cast\nif (obj instanceof Integer) {\n    Integer num = (Integer) obj;\n    System.out.println(num);\n} else {\n    System.out.println(\"Tipo real: \" + obj.getClass().getSimpleName());\n}",
        "tip": "Usa instanceof antes de cualquier cast para evitar este error.",
    },
    {
        "num": "36", "lenguaje": "Java",
        "nombre": "ArithmeticException — Division entera entre cero",
        "descripcion": "En Java, dividir un entero entre 0 lanza ArithmeticException. A diferencia de double, los int no producen Infinity.",
        "error": "public class Main {\n    public static void main(String[] args) {\n        int a = 10, b = 0;\n        System.out.println(a / b);   // ArithmeticException: / by zero\n    }\n}",
        "solucion": "public class Main {\n    public static void main(String[] args) {\n        int a = 10, b = 0;\n\n        if (b != 0) {\n            System.out.println(a / b);\n        } else {\n            System.out.println(\"No se puede dividir entre cero\");\n        }\n    }\n}",
        "tip": "Valida que el divisor sea distinto de 0 antes de dividir enteros en Java.",
    },
    {
        "num": "37", "lenguaje": "Java",
        "nombre": "StringIndexOutOfBoundsException — Indice invalido en String",
        "descripcion": "Ocurre cuando se intenta acceder a una posicion inexistente dentro de un String usando charAt() u otros metodos.",
        "error": "public class Main {\n    public static void main(String[] args) {\n        String texto = \"Hola\";\n        char c = texto.charAt(10);   // StringIndexOutOfBoundsException\n    }\n}",
        "solucion": "public class Main {\n    public static void main(String[] args) {\n        String texto = \"Hola\";\n        int indice = 10;\n\n        if (indice >= 0 && indice < texto.length()) {\n            System.out.println(texto.charAt(indice));\n        } else {\n            System.out.println(\"Indice fuera de rango. Longitud: \" + texto.length());\n        }\n    }\n}",
        "tip": "Verifica siempre que el indice sea menor que texto.length() antes de usar charAt().",
    },
    {
        "num": "38", "lenguaje": "Java",
        "nombre": "IllegalArgumentException — Argumento invalido",
        "descripcion": "Se lanza cuando un metodo recibe un argumento que no cumple con las condiciones esperadas.",
        "error": "public class Rectangulo {\n    int ancho;\n\n    void setAncho(int a) {\n        this.ancho = a;   // acepta valores negativos: error logico\n    }\n}",
        "solucion": "public class Rectangulo {\n    int ancho;\n\n    void setAncho(int a) {\n        if (a <= 0) {\n            throw new IllegalArgumentException(\"El ancho debe ser positivo: \" + a);\n        }\n        this.ancho = a;\n    }\n}",
        "tip": "Valida los parametros al inicio de cada metodo y lanza IllegalArgumentException si son invalidos.",
    },
    {
        "num": "39", "lenguaje": "Java",
        "nombre": "ConcurrentModificationException — Modificar coleccion al iterar",
        "descripcion": "Ocurre cuando modificas un ArrayList u otra coleccion mientras la recorres con un for-each.",
        "error": "List<String> lista = new ArrayList<>(List.of(\"a\",\"b\",\"c\"));\n\nfor (String s : lista) {\n    if (s.equals(\"b\")) {\n        lista.remove(s);   // ConcurrentModificationException\n    }\n}",
        "solucion": "List<String> lista = new ArrayList<>(List.of(\"a\",\"b\",\"c\"));\n\n// Usar Iterator para eliminar de forma segura\nIterator<String> it = lista.iterator();\nwhile (it.hasNext()) {\n    if (it.next().equals(\"b\")) {\n        it.remove();   // seguro\n    }\n}\nSystem.out.println(lista);   // [a, c]",
        "tip": "Para eliminar elementos al iterar, usa Iterator.remove() o removeIf().",
    },
    {
        "num": "40", "lenguaje": "Java",
        "nombre": "OutOfMemoryError — Sin memoria en el heap",
        "descripcion": "La JVM se queda sin memoria en el heap. Suele ocurrir por fugas de memoria o colecciones que crecen indefinidamente.",
        "error": "import java.util.ArrayList;\nimport java.util.List;\n\npublic class Main {\n    public static void main(String[] args) {\n        List<int[]> lista = new ArrayList<>();\n        while (true) {\n            lista.add(new int[1_000_000]);   // OutOfMemoryError\n        }\n    }\n}",
        "solucion": "// Liberar referencias cuando no se necesiten\nimport java.util.ArrayList;\nimport java.util.List;\n\npublic class Main {\n    public static void main(String[] args) {\n        List<int[]> lista = new ArrayList<>();\n        for (int i = 0; i < 10; i++) {\n            lista.add(new int[1_000]);\n        }\n        lista.clear();   // liberar memoria\n        System.out.println(\"Procesado con exito\");\n    }\n}",
        "tip": "Libera listas grandes con clear() o asignando null cuando ya no las necesitas.",
    },
    {
        "num": "41", "lenguaje": "Java",
        "nombre": "FileNotFoundException — Archivo no encontrado",
        "descripcion": "Ocurre al intentar abrir un FileReader o FileInputStream con una ruta de archivo que no existe.",
        "error": "import java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        FileReader fr = new FileReader(\"datos.txt\");   // FileNotFoundException\n    }\n}",
        "solucion": "import java.io.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        File archivo = new File(\"datos.txt\");\n\n        if (archivo.exists()) {\n            try (FileReader fr = new FileReader(archivo)) {\n                // leer archivo\n            } catch (IOException e) {\n                System.out.println(\"Error al leer: \" + e.getMessage());\n            }\n        } else {\n            System.out.println(\"El archivo no existe\");\n        }\n    }\n}",
        "tip": "Verifica archivo.exists() antes de abrirlo, o maneja FileNotFoundException con try-catch.",
    },
    {
        "num": "42", "lenguaje": "Java",
        "nombre": "IOException — Error de entrada/salida",
        "descripcion": "Excepcion general para errores de I/O: lectura, escritura, cierre de streams. Es una excepcion verificada (checked) en Java.",
        "error": "public class Main {\n    public static void main(String[] args) {\n        // Error: IOException es checked y debe declararse o manejarse\n        FileWriter fw = new FileWriter(\"salida.txt\");\n        fw.write(\"Hola\");\n        fw.close();\n    }\n}",
        "solucion": "import java.io.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        try (FileWriter fw = new FileWriter(\"salida.txt\")) {\n            fw.write(\"Hola\");\n            System.out.println(\"Archivo escrito correctamente\");\n        } catch (IOException e) {\n            System.out.println(\"Error de I/O: \" + e.getMessage());\n        }\n    }\n}",
        "tip": "Usa try-with-resources para cerrar automaticamente FileWriter, FileReader y similares.",
    },
    {
        "num": "43", "lenguaje": "Java",
        "nombre": "UnsupportedOperationException — Operacion no permitida",
        "descripcion": "Ocurre al intentar modificar una lista inmutable creada con List.of() o Arrays.asList().",
        "error": "import java.util.*;\n\nList<String> lista = List.of(\"a\", \"b\", \"c\");\nlista.add(\"d\");      // UnsupportedOperationException\nlista.remove(\"a\");   // UnsupportedOperationException",
        "solucion": "import java.util.*;\n\n// Crear lista mutable desde una inmutable\nList<String> lista = new ArrayList<>(List.of(\"a\", \"b\", \"c\"));\nlista.add(\"d\");\nlista.remove(\"a\");\nSystem.out.println(lista);   // [b, c, d]",
        "tip": "List.of() y Arrays.asList() retornan listas inmutables. Envuelve en new ArrayList<>() para mutarlas.",
    },
    {
        "num": "44", "lenguaje": "Java",
        "nombre": "IllegalStateException — Estado invalido del objeto",
        "descripcion": "Se lanza cuando un metodo es llamado en un momento inadecuado segun el estado interno del objeto.",
        "error": "import java.util.*;\n\nList<String> lista = new ArrayList<>(List.of(\"a\", \"b\"));\nIterator<String> it = lista.iterator();\nit.remove();   // IllegalStateException: no se ha llamado next() aun",
        "solucion": "import java.util.*;\n\nList<String> lista = new ArrayList<>(List.of(\"a\", \"b\"));\nIterator<String> it = lista.iterator();\n\nif (it.hasNext()) {\n    it.next();     // avanzar primero\n    it.remove();   // ahora si es valido\n}\nSystem.out.println(lista);   // [b]",
        "tip": "Llama siempre next() antes de remove() en un Iterator.",
    },
    {
        "num": "45", "lenguaje": "Java",
        "nombre": "NoSuchElementException — Elemento inexistente en coleccion",
        "descripcion": "Ocurre al llamar next() en un Iterator o Scanner cuando no hay mas elementos disponibles.",
        "error": "import java.util.*;\n\nList<Integer> nums = new ArrayList<>(List.of(1, 2));\nIterator<Integer> it = nums.iterator();\nit.next();  // 1\nit.next();  // 2\nit.next();  // NoSuchElementException",
        "solucion": "import java.util.*;\n\nList<Integer> nums = new ArrayList<>(List.of(1, 2));\nIterator<Integer> it = nums.iterator();\n\nwhile (it.hasNext()) {      // verificar antes de llamar next()\n    System.out.println(it.next());\n}",
        "tip": "Usa siempre hasNext() antes de next() para evitar NoSuchElementException.",
    },
    {
        "num": "46", "lenguaje": "Java",
        "nombre": "ExceptionInInitializerError — Error en bloque estatico",
        "descripcion": "Ocurre cuando una excepcion no manejada se lanza durante la inicializacion estatica de una clase.",
        "error": "public class Config {\n    static int LIMITE = Integer.parseInt(\"abc\");   // NumberFormatException\n    // -> ExceptionInInitializerError al cargar la clase\n}",
        "solucion": "public class Config {\n    static int LIMITE;\n\n    static {\n        try {\n            LIMITE = Integer.parseInt(\"abc\");\n        } catch (NumberFormatException e) {\n            System.out.println(\"Valor invalido, usando defecto\");\n            LIMITE = 100;   // valor por defecto seguro\n        }\n    }\n}",
        "tip": "Envuelve el codigo de bloques static{} en try/catch para evitar errores en la carga de la clase.",
    },
    {
        "num": "47", "lenguaje": "Java",
        "nombre": "AssertionError — Asercion fallida",
        "descripcion": "Se lanza cuando una instruccion assert falla. Las aserciones deben habilitarse con la bandera -ea al ejecutar Java.",
        "error": "public class Main {\n    public static void main(String[] args) {\n        int edad = -5;\n        assert edad >= 0 : \"Edad no puede ser negativa\";   // AssertionError\n        System.out.println(edad);\n    }\n}",
        "solucion": "public class Main {\n    public static void main(String[] args) {\n        int edad = -5;\n\n        if (edad < 0) {\n            throw new IllegalArgumentException(\"Edad no puede ser negativa: \" + edad);\n        }\n        System.out.println(edad);\n    }\n}",
        "tip": "Usa assert solo para debugging interno. Para validaciones de produccion, usa if + throw.",
    },
    {
        "num": "48", "lenguaje": "Java",
        "nombre": "ParseException — Error al parsear fecha",
        "descripcion": "Ocurre cuando SimpleDateFormat no puede interpretar un String como fecha porque el formato no coincide.",
        "error": "import java.text.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        SimpleDateFormat sdf = new SimpleDateFormat(\"dd/MM/yyyy\");\n        sdf.parse(\"2024-12-25\");   // ParseException: formato incorrecto\n    }\n}",
        "solucion": "import java.text.*;\nimport java.util.Date;\n\npublic class Main {\n    public static void main(String[] args) {\n        SimpleDateFormat sdf = new SimpleDateFormat(\"yyyy-MM-dd\");   // formato correcto\n        try {\n            Date fecha = sdf.parse(\"2024-12-25\");\n            System.out.println(fecha);\n        } catch (ParseException e) {\n            System.out.println(\"Formato de fecha invalido: \" + e.getMessage());\n        }\n    }\n}",
        "tip": "El patron en SimpleDateFormat DEBE coincidir exactamente con el formato del String a parsear.",
    },
    {
        "num": "49", "lenguaje": "Java",
        "nombre": "ClassNotFoundException — Clase no encontrada en classpath",
        "descripcion": "Ocurre cuando Class.forName() no puede encontrar la clase especificada porque no esta en el classpath del proyecto.",
        "error": "public class Main {\n    public static void main(String[] args) throws Exception {\n        Class<?> c = Class.forName(\"com.mysql.jdbc.Driver\");   // ClassNotFoundException\n    }\n}",
        "solucion": "// 1. Agregar el JAR del driver al classpath del proyecto\n// 2. En Maven, agregar la dependencia en pom.xml:\n// <dependency>\n//   <groupId>mysql</groupId>\n//   <artifactId>mysql-connector-java</artifactId>\n//   <version>8.0.33</version>\n// </dependency>\n\npublic class Main {\n    public static void main(String[] args) {\n        try {\n            Class<?> c = Class.forName(\"com.mysql.cj.jdbc.Driver\");\n            System.out.println(\"Driver encontrado: \" + c.getName());\n        } catch (ClassNotFoundException e) {\n            System.out.println(\"Driver no encontrado. Agrega el JAR al classpath.\");\n        }\n    }\n}",
        "tip": "Verifica que el JAR de la dependencia este agregado al proyecto y que el nombre de la clase sea correcto.",
    },
    {
        "num": "50", "lenguaje": "Java",
        "nombre": "InterruptedException — Hilo interrumpido durante espera",
        "descripcion": "Se lanza cuando un hilo bloqueado en sleep(), wait() o join() es interrumpido por otro hilo.",
        "error": "public class Main {\n    public static void main(String[] args) throws InterruptedException {\n        System.out.println(\"Esperando...\");\n        Thread.sleep(2000);   // si el hilo es interrumpido -> InterruptedException\n        System.out.println(\"Listo\");\n    }\n}",
        "solucion": "public class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Esperando...\");\n        try {\n            Thread.sleep(2000);\n            System.out.println(\"Listo\");\n        } catch (InterruptedException e) {\n            Thread.currentThread().interrupt();   // restaurar estado de interrupcion\n            System.out.println(\"El hilo fue interrumpido\");\n        }\n    }\n}",
        "tip": "Tras capturar InterruptedException, llama Thread.currentThread().interrupt() para propagar el estado.",
    },
    {
        "num": "51", "lenguaje": "Java",
        "nombre": "SQLException — Error en consulta SQL",
        "descripcion": "Se lanza cuando hay un error al conectar a una base de datos o al ejecutar una consulta SQL incorrecta.",
        "error": "import java.sql.*;\n\n// SQL con error de sintaxis\nStatement stmt = conn.createStatement();\nResultSet rs = stmt.executeQuery(\"SELEC * FROM usuarios\");  // SQLException",
        "solucion": "import java.sql.*;\n\ntry (Connection conn = DriverManager.getConnection(url, user, pass);\n     Statement stmt = conn.createStatement()) {\n\n    ResultSet rs = stmt.executeQuery(\"SELECT * FROM usuarios\");\n    while (rs.next()) {\n        System.out.println(rs.getString(\"nombre\"));\n    }\n} catch (SQLException e) {\n    System.out.println(\"Error SQL [\" + e.getErrorCode() + \"]: \" + e.getMessage());\n}",
        "tip": "Usa PreparedStatement en lugar de Statement para evitar errores de sintaxis e inyeccion SQL.",
    },
    {
        "num": "52", "lenguaje": "Java",
        "nombre": "NegativeArraySizeException — Tamano de arreglo negativo",
        "descripcion": "Ocurre cuando se intenta crear un arreglo con un tamano negativo.",
        "error": "public class Main {\n    public static void main(String[] args) {\n        int tamano = -5;\n        int[] arreglo = new int[tamano];   // NegativeArraySizeException\n    }\n}",
        "solucion": "public class Main {\n    public static void main(String[] args) {\n        int tamano = -5;\n\n        if (tamano < 0) {\n            throw new IllegalArgumentException(\"Tamano invalido: \" + tamano);\n        }\n        int[] arreglo = new int[tamano];\n        System.out.println(\"Arreglo creado con \" + arreglo.length + \" elementos\");\n    }\n}",
        "tip": "Valida que el tamano sea >= 0 antes de crear un arreglo.",
    },
    {
        "num": "53", "lenguaje": "Java",
        "nombre": "EmptyStackException — Pila vacia",
        "descripcion": "Ocurre al llamar pop() o peek() en un objeto Stack que no tiene elementos.",
        "error": "import java.util.Stack;\n\npublic class Main {\n    public static void main(String[] args) {\n        Stack<Integer> pila = new Stack<>();\n        pila.push(1);\n        pila.pop();     // 1\n        pila.pop();     // EmptyStackException\n    }\n}",
        "solucion": "import java.util.Stack;\n\npublic class Main {\n    public static void main(String[] args) {\n        Stack<Integer> pila = new Stack<>();\n        pila.push(1);\n\n        if (!pila.isEmpty()) {\n            System.out.println(pila.pop());   // 1\n        }\n        if (!pila.isEmpty()) {\n            System.out.println(pila.pop());\n        } else {\n            System.out.println(\"La pila esta vacia\");\n        }\n    }\n}",
        "tip": "Siempre verifica !pila.isEmpty() antes de llamar pop() o peek().",
    },
    {
        "num": "54", "lenguaje": "Java",
        "nombre": "InputMismatchException — Tipo de entrada inesperado en Scanner",
        "descripcion": "Ocurre cuando Scanner.nextInt() (u otro metodo tipado) encuentra un valor del tipo incorrecto en la entrada.",
        "error": "import java.util.Scanner;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int numero = sc.nextInt();   // InputMismatchException si el usuario escribe \"hola\"\n    }\n}",
        "solucion": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        System.out.print(\"Ingresa un numero: \");\n\n        try {\n            int numero = sc.nextInt();\n            System.out.println(\"Recibido: \" + numero);\n        } catch (InputMismatchException e) {\n            System.out.println(\"Entrada invalida. Se esperaba un entero.\");\n        }\n    }\n}",
        "tip": "Usa sc.hasNextInt() para verificar el tipo antes de leer, o maneja InputMismatchException con try/catch.",
    },
    {
        "num": "55", "lenguaje": "Java",
        "nombre": "ArrayStoreException — Tipo incorrecto en arreglo de objetos",
        "descripcion": "Ocurre al intentar guardar un objeto de tipo incompatible en un arreglo tipado.",
        "error": "Object[] arreglo = new String[3];\narreglo[0] = \"Hola\";    // ok\narreglo[1] = 42;         // ArrayStoreException: Integer en String[]",
        "solucion": "// Opcion 1: usar el tipo correcto\nString[] arreglo = new String[3];\narreglo[0] = \"Hola\";\narreglo[1] = \"42\";   // String, no int\n\n// Opcion 2: si se necesitan tipos mixtos\nObject[] mixto = new Object[3];\nmixto[0] = \"Hola\";\nmixto[1] = 42;   // ok: Object acepta cualquier referencia",
        "tip": "Declara el arreglo con el tipo exacto que almacenara, o usa Object[] si los tipos seran mixtos.",
    },
    {
        "num": "56", "lenguaje": "Java",
        "nombre": "InfiniteLoop — Bucle sin condicion de salida",
        "descripcion": "Un while o for que nunca actualiza la variable de control queda en ejecucion infinita y congela el programa.",
        "error": "public class Main {\n    public static void main(String[] args) {\n        int i = 0;\n        while (i < 5) {\n            System.out.println(i);\n            // falta: i++;  -> bucle infinito\n        }\n    }\n}",
        "solucion": "public class Main {\n    public static void main(String[] args) {\n        int i = 0;\n        while (i < 5) {\n            System.out.println(i);\n            i++;   // actualizar la variable de control\n        }\n    }\n}",
        "tip": "Asegurate de que la variable de control del while cambie en cada iteracion para que la condicion sea falsa en algun momento.",
    },
    {
        "num": "57", "lenguaje": "Java",
        "nombre": "WrongReturnType — Tipo de retorno incorrecto",
        "descripcion": "Error de compilacion que ocurre cuando el tipo declarado en la firma del metodo no coincide con el valor retornado.",
        "error": "public class Main {\n    // declara int pero retorna String -> error de compilacion\n    static int obtenerMensaje() {\n        return \"Hola\";   // incompatible types: String cannot be converted to int\n    }\n}",
        "solucion": "public class Main {\n    // Opcion A: cambiar el tipo de retorno\n    static String obtenerMensaje() {\n        return \"Hola\";\n    }\n\n    // Opcion B: retornar el tipo correcto\n    static int obtenerNumero() {\n        return 42;\n    }\n}",
        "tip": "El tipo de retorno en la firma del metodo debe coincidir exactamente con el tipo del valor retornado.",
    },
    {
        "num": "58", "lenguaje": "Java",
        "nombre": "MissingReturnStatement — Falta instruccion return",
        "descripcion": "Error de compilacion que ocurre cuando un metodo no void no garantiza retornar un valor en todos los caminos de ejecucion.",
        "error": "public class Main {\n    static String clasificar(int n) {\n        if (n > 0) {\n            return \"positivo\";\n        }\n        // falta return para n <= 0 -> error de compilacion\n    }\n}",
        "solucion": "public class Main {\n    static String clasificar(int n) {\n        if (n > 0) {\n            return \"positivo\";\n        } else if (n < 0) {\n            return \"negativo\";\n        } else {\n            return \"cero\";   // todos los casos cubiertos\n        }\n    }\n}",
        "tip": "Java requiere que todos los caminos posibles de un metodo no void terminen con un return.",
    },
    {
        "num": "59", "lenguaje": "Java",
        "nombre": "DeadCode — Codigo inalcanzable despues de return",
        "descripcion": "Error de compilacion que ocurre cuando hay sentencias escritas despues de un return, throw u otro salto incondicional.",
        "error": "public class Main {\n    static int calcular(int x) {\n        return x * 2;\n        System.out.println(\"Listo\");   // unreachable statement\n        return 0;\n    }\n}",
        "solucion": "public class Main {\n    static int calcular(int x) {\n        int resultado = x * 2;\n        System.out.println(\"Listo\");   // antes del return\n        return resultado;\n    }\n}",
        "tip": "Mueve cualquier logica que deba ejecutarse ANTES del return, no despues.",
    },
    {
        "num": "60", "lenguaje": "Java",
        "nombre": "EqualsVsDoubleEquals — Comparar Strings con == en lugar de equals()",
        "descripcion": "En Java, == compara referencias de memoria, no el contenido. Dos Strings con el mismo texto pueden estar en distintas posiciones de memoria.",
        "error": "public class Main {\n    public static void main(String[] args) {\n        String a = new String(\"hola\");\n        String b = new String(\"hola\");\n\n        if (a == b) {              // false: distintas referencias\n            System.out.println(\"Son iguales\");\n        } else {\n            System.out.println(\"Son distintos\");  // se imprime esto\n        }\n    }\n}",
        "solucion": "public class Main {\n    public static void main(String[] args) {\n        String a = new String(\"hola\");\n        String b = new String(\"hola\");\n\n        if (a.equals(b)) {         // true: compara contenido\n            System.out.println(\"Son iguales\");  // se imprime esto\n        } else {\n            System.out.println(\"Son distintos\");\n        }\n    }\n}",
        "tip": "Para Strings y objetos, usa siempre .equals() en lugar de ==. Reserva == para tipos primitivos (int, double, etc.).",
    },
]

# ── Paleta de colores ─────────────────────────────────────────
BG         = "#ffffff"
SIDEBAR_BG = "#f7f7f7"
BORDER     = "#e2e2e2"
TEXT       = "#1a1a1a"
SUBTEXT    = "#777777"
PY_COLOR   = "#2b5ea7"
JAVA_COLOR = "#c25400"
ERROR_BG   = "#fff5f5"
ERROR_FG   = "#b91c1c"
OK_BG      = "#f0fff4"
OK_FG      = "#15803d"
TIP_BG     = "#fffbeb"
TIP_FG     = "#92400e"
CODE_BG    = "#f8f8f8"
CODE_FG    = "#222222"
SEL_BG     = "#e8f0fe"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Repositorio de Errores — Python & Java")
        self.geometry("1020x680")
        self.minsize(800, 500)
        self.configure(bg=BG)
        self.filtro = tk.StringVar(value="Todos")
        self.sel_frame = None
        self._build()

    # ── Construcción principal ────────────────────────────────
    def _build(self):
        self._top_bar()
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)
        self._sidebar(body)
        tk.Frame(body, bg=BORDER, width=1).pack(side="left", fill="y")
        self._detail_panel(body)
        self._render_lista(errores)
        self._bienvenida()

    def _top_bar(self):
        bar = tk.Frame(self, bg=BG, padx=20, pady=12)
        bar.pack(fill="x")

        tk.Label(bar, text="Repositorio de Errores",
                 font=("Helvetica", 16, "bold"),
                 bg=BG, fg=TEXT).pack(side="left")
        tk.Label(bar, text="Python & Java · Principiantes",
                 font=("Helvetica", 10), bg=BG, fg=SUBTEXT).pack(side="left", padx=10)

        # Filtros radio
        filter_box = tk.Frame(bar, bg=BG)
        filter_box.pack(side="right")
        for label, val in [("Todos", "Todos"), ("Python 🐍", "Python"), ("Java ☕", "Java")]:
            rb = tk.Radiobutton(filter_box, text=label, variable=self.filtro,
                                value=val, command=self._filtrar,
                                bg=BG, fg=TEXT, selectcolor=BG,
                                activebackground=BG, font=("Helvetica", 10),
                                cursor="hand2")
            rb.pack(side="left", padx=6)

    # ── Sidebar ───────────────────────────────────────────────
    def _sidebar(self, parent):
        side = tk.Frame(parent, bg=SIDEBAR_BG, width=260)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        # Canvas + scrollbar
        canvas = tk.Canvas(side, bg=SIDEBAR_BG, highlightthickness=0)
        sb = ttk.Scrollbar(side, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.list_frame = tk.Frame(canvas, bg=SIDEBAR_BG)
        win = canvas.create_window((0, 0), window=self.list_frame, anchor="nw")

        def _resize(ev):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win, width=canvas.winfo_width())
        self.list_frame.bind("<Configure>", _resize)

        def _scroll(ev):
            canvas.yview_scroll(int(-1 * (ev.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _scroll)

    # ── Panel detalle ─────────────────────────────────────────
    def _detail_panel(self, parent):
        det = tk.Frame(parent, bg=BG)
        det.pack(side="left", fill="both", expand=True)

        self.det_canvas = tk.Canvas(det, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(det, orient="vertical", command=self.det_canvas.yview)
        self.det_canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.det_canvas.pack(side="left", fill="both", expand=True)

        self.det_inner = tk.Frame(self.det_canvas, bg=BG)
        win = self.det_canvas.create_window((0, 0), window=self.det_inner, anchor="nw")

        def _resize(ev):
            self.det_canvas.configure(scrollregion=self.det_canvas.bbox("all"))
            self.det_canvas.itemconfig(win, width=self.det_canvas.winfo_width())
        self.det_inner.bind("<Configure>", _resize)

        def _scroll(ev):
            self.det_canvas.yview_scroll(int(-1 * (ev.delta / 120)), "units")
        self.det_canvas.bind("<MouseWheel>", _scroll)

    # ── Filtro ────────────────────────────────────────────────
    def _filtrar(self):
        f = self.filtro.get()
        subset = errores if f == "Todos" else [e for e in errores if e["lenguaje"] == f]
        self.sel_frame = None
        self._render_lista(subset)
        self._bienvenida()

    def _render_lista(self, subset):
        for w in self.list_frame.winfo_children():
            w.destroy()
        for e in subset:
            self._item(e)

    def _item(self, e):
        dot_color = PY_COLOR if e["lenguaje"] == "Python" else JAVA_COLOR

        row = tk.Frame(self.list_frame, bg=SIDEBAR_BG, cursor="hand2")
        row.pack(fill="x")

        inner = tk.Frame(row, bg=SIDEBAR_BG, padx=12, pady=9)
        inner.pack(fill="x")

        top = tk.Frame(inner, bg=SIDEBAR_BG)
        top.pack(fill="x")

        dot = tk.Label(top, text="●", font=("Helvetica", 7),
                       bg=SIDEBAR_BG, fg=dot_color)
        dot.pack(side="left", padx=(0, 5))

        title = tk.Label(top, text=f"[{e['num']}] {e['nombre']}",
                         font=("Helvetica", 9, "bold"), bg=SIDEBAR_BG, fg=TEXT,
                         wraplength=200, justify="left", anchor="w")
        title.pack(side="left", fill="x")

        lang_lbl = tk.Label(inner, text=e["lenguaje"],
                            font=("Helvetica", 8), bg=SIDEBAR_BG, fg=SUBTEXT, anchor="w")
        lang_lbl.pack(fill="x")

        tk.Frame(row, bg=BORDER, height=1).pack(fill="x")

        all_widgets = [row, inner, top, dot, title, lang_lbl]

        def on_enter(ev, ws=all_widgets):
            for w in ws:
                try: w.configure(bg="#ececec")
                except: pass

        def on_leave(ev, ws=all_widgets, sel_r=row):
            bg = SEL_BG if self.sel_frame == sel_r else SIDEBAR_BG
            for w in ws:
                try: w.configure(bg=bg)
                except: pass

        def on_click(ev, err=e, sel_r=row, ws=all_widgets):
            if self.sel_frame and self.sel_frame != sel_r:
                for w in self.sel_frame.winfo_children():
                    self._reset_bg(w, SIDEBAR_BG)
                self._reset_bg(self.sel_frame, SIDEBAR_BG)
            self.sel_frame = sel_r
            for w in ws:
                try: w.configure(bg=SEL_BG)
                except: pass
            self._mostrar(err)

        for w in all_widgets:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

    def _reset_bg(self, widget, color):
        try: widget.configure(bg=color)
        except: pass
        for child in widget.winfo_children():
            self._reset_bg(child, color)

    # ── Panel detalle ─────────────────────────────────────────
    def _bienvenida(self):
        for w in self.det_inner.winfo_children():
            w.destroy()
        f = tk.Frame(self.det_inner, bg=BG, padx=40, pady=80)
        f.pack(fill="both", expand=True)
        tk.Label(f, text="📚", font=("Helvetica", 40), bg=BG).pack(pady=(0, 12))
        tk.Label(f, text="Selecciona un error de la lista",
                 font=("Helvetica", 13), bg=BG, fg=SUBTEXT).pack()
        tk.Label(f, text="para ver cómo se produce y cómo corregirlo.",
                 font=("Helvetica", 10), bg=BG, fg=SUBTEXT).pack(pady=4)

    def _mostrar(self, e):
        for w in self.det_inner.winfo_children():
            w.destroy()

        lang_color = PY_COLOR if e["lenguaje"] == "Python" else JAVA_COLOR
        out = tk.Frame(self.det_inner, bg=BG, padx=28, pady=22)
        out.pack(fill="both", expand=True)

        # Cabecera
        head = tk.Frame(out, bg=BG)
        head.pack(fill="x", pady=(0, 6))
        tk.Label(head, text=e["lenguaje"], font=("Helvetica", 9, "bold"),
                 bg=lang_color, fg="white", padx=8, pady=3).pack(side="left")
        tk.Label(head, text=f"  Error {e['num']}",
                 font=("Helvetica", 9), bg=BG, fg=SUBTEXT).pack(side="left")

        tk.Label(out, text=e["nombre"], font=("Helvetica", 14, "bold"),
                 bg=BG, fg=TEXT, anchor="w", wraplength=640,
                 justify="left").pack(fill="x", pady=(0, 4))
        tk.Frame(out, bg=BORDER, height=1).pack(fill="x", pady=(2, 14))

        # Descripcion
        tk.Label(out, text="¿Cómo se produce?",
                 font=("Helvetica", 10, "bold"), bg=BG, fg=SUBTEXT,
                 anchor="w").pack(fill="x")
        tk.Label(out, text=e["descripcion"], font=("Helvetica", 10),
                 bg=BG, fg=TEXT, wraplength=640, justify="left",
                 anchor="w").pack(fill="x", pady=(2, 14))

        # Bloque error
        self._bloque_codigo(out, "❌  Código con error",
                            e["error"], ERROR_BG, ERROR_FG, "#fca5a5")
        # Bloque solucion
        self._bloque_codigo(out, "✅  Corrección",
                            e["solucion"], OK_BG, OK_FG, "#86efac")

        # Tip
        tip = tk.Frame(out, bg=TIP_BG, highlightbackground="#fcd34d",
                       highlightthickness=1)
        tip.pack(fill="x", pady=(4, 0))
        tk.Label(tip, text=f"💡  {e['tip']}",
                 font=("Helvetica", 10), bg=TIP_BG, fg=TIP_FG,
                 padx=14, pady=10, wraplength=620,
                 justify="left", anchor="w").pack(fill="x")

        self.det_canvas.yview_moveto(0)

    def _bloque_codigo(self, parent, titulo, codigo, bg, fg_title, border):
        tk.Label(parent, text=titulo, font=("Helvetica", 10, "bold"),
                 bg=BG, fg=fg_title, anchor="w").pack(fill="x", pady=(0, 4))
        box = tk.Frame(parent, bg=CODE_BG,
                       highlightbackground=border, highlightthickness=1)
        box.pack(fill="x", pady=(0, 14))
        tk.Label(box, text=codigo, font=("Courier", 9),
                 bg=CODE_BG, fg=CODE_FG, justify="left",
                 anchor="nw", padx=14, pady=12).pack(fill="x")


if __name__ == "__main__":
    app = App()
    app.mainloop()
