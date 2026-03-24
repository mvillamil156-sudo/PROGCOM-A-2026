"""
╔══════════════════════════════════════════════════════════════════════════════╗
║   OPTIMIZADOR DE SISTEMA HÍBRIDO SOLAR-BATERÍA                              ║
║   Ingeniería en Energía y Sostenibilidad                                    ║
║                                                                              ║
║   Problema: Dimensionar un sistema fotovoltaico con almacenamiento           ║
║   para minimizar el costo total y maximizar la autosuficiencia energética.  ║
╚══════════════════════════════════════════════════════════════════════════════╝

DESCRIPCIÓN DEL PROBLEMA
─────────────────────────
Un usuario (hogar o PYME) quiere instalar paneles solares con baterías para
reducir su dependencia de la red eléctrica. Debe decidir:
  → ¿Cuántos paneles solares instalar?
  → ¿Qué capacidad de batería necesita?

El objetivo es encontrar la combinación que minimice el Costo Anual Total (CAT),
que incluye: amortización del sistema + costo de energía comprada a la red.

METODOLOGÍA
────────────
1. Se genera un perfil de consumo horario realista (8760 horas/año)
2. Se genera un perfil de irradiancia solar horaria con variación estacional
3. Para cada combinación (paneles × baterías), se simula hora a hora:
   - La generación fotovoltaica
   - La carga/descarga de la batería
   - La energía comprada/vendida a la red
4. Se calcula el CAT para cada configuración
5. Se identifica la configuración óptima
"""

import math
import random


# ─────────────────────────────────────────────────────────────────────────────
# PARÁMETROS DEL SISTEMA
# ─────────────────────────────────────────────────────────────────────────────

# Panel solar (típico panel monocristalino 400W)
PANEL_POTENCIA_W = 400          # Potencia pico por panel (W)
PANEL_EFICIENCIA = 0.20         # Eficiencia del panel (20%)
PANEL_AREA_M2 = 2.0             # Área por panel (m²)
PANEL_COSTO_USD = 250           # Costo por panel instalado (USD)
PANEL_VIDA_ANOS = 25            # Vida útil del panel (años)
PANEL_DEGRADACION_ANUAL = 0.005 # Degradación anual (0.5%)

# Batería (LiFePO4 típica)
BAT_COSTO_USD_KWH = 350         # Costo por kWh de capacidad (USD)
BAT_VIDA_ANOS = 10              # Vida útil de la batería (años)
BAT_EFICIENCIA_CARGA = 0.95     # Eficiencia de carga (95%)
BAT_EFICIENCIA_DESCARGA = 0.95  # Eficiencia de descarga (95%)
BAT_SOC_MIN = 0.15              # Estado de carga mínimo (15%) — protección
BAT_SOC_MAX = 0.95              # Estado de carga máximo (95%) — protección
BAT_C_RATE_MAX = 0.5            # Tasa máxima de carga/descarga (0.5C)

# Inversor
INVERSOR_EFICIENCIA = 0.97      # Eficiencia del inversor (97%)
INVERSOR_COSTO_USD = 1500       # Costo fijo del inversor (USD)
INVERSOR_VIDA_ANOS = 12         # Vida útil del inversor (años)

# Economía
TASA_DESC_ANUAL = 0.08          # Tasa de descuento anual (8%)
PRECIO_COMPRA_USD_KWH = 0.18    # Precio de compra a la red (USD/kWh)
PRECIO_VENTA_USD_KWH = 0.06     # Precio de venta a la red (USD/kWh — net metering)
HORIZONTE_ANOS = 25             # Horizonte de análisis (años)
EMISION_CO2_KG_KWH = 0.400     # Factor de emisión de la red (kg CO₂/kWh)

# Ubicación (Colombia — zona de alta irradiancia)
IRRADIANCIA_MEDIA_ANUAL = 5.2   # Horas solares pico promedio diarias (HSP)
LATITUD_GRADOS = 7.0            # Latitud de Bucaramanga, Colombia

# Rango de optimización
MIN_PANELES = 2
MAX_PANELES = 30
PASO_PANELES = 2

MIN_BAT_KWH = 0
MAX_BAT_KWH = 40
PASO_BAT_KWH = 5


# ─────────────────────────────────────────────────────────────────────────────
# GENERACIÓN DE PERFILES HORARIOS (8760 horas)
# ─────────────────────────────────────────────────────────────────────────────

def generar_perfil_consumo(semilla=42):
    """
    Genera un perfil de consumo eléctrico horario para un año completo.
    Modela un hogar colombiano de clase media (consumo anual ~3,500 kWh/año).
    
    Incluye:
    - Variación por hora del día (mañana/tarde/noche)
    - Variación día de semana vs fin de semana
    - Variación estacional leve (más ventilación en verano)
    - Ruido aleatorio reproducible
    """
    random.seed(semilla)
    consumo_horario = []
    
    # Perfil base por hora del día (kW) — hogar típico
    perfil_dia_semana = [
        0.25, 0.20, 0.18, 0.18, 0.22, 0.45,  # 00-05h (madrugada, algo de noche)
        0.80, 1.20, 0.90, 0.60, 0.55, 0.65,  # 06-11h (mañana, desayuno)
        0.70, 0.60, 0.55, 0.60, 0.75, 1.10,  # 12-17h (tarde, almuerzo)
        1.30, 1.50, 1.20, 0.90, 0.65, 0.40   # 18-23h (noche, cena, TV)
    ]
    
    perfil_fin_semana = [
        0.35, 0.28, 0.22, 0.20, 0.22, 0.35,
        0.60, 0.90, 1.10, 1.00, 0.90, 0.95,
        1.00, 0.85, 0.80, 0.85, 0.90, 1.05,
        1.20, 1.40, 1.30, 1.10, 0.85, 0.55
    ]
    
    for dia in range(365):
        es_fin_semana = (dia % 7) >= 5
        mes = int(dia / 30.44)
        factor_estacional = 1.0 + 0.08 * math.sin(2 * math.pi * (mes - 6) / 12)
        
        perfil = perfil_fin_semana if es_fin_semana else perfil_dia_semana
        
        for hora in range(24):
            base = perfil[hora]
            ruido = random.gauss(1.0, 0.08)
            consumo = base * factor_estacional * ruido
            consumo = max(0.1, consumo)
            consumo_horario.append(consumo)
    
    return consumo_horario


def generar_perfil_irradiancia(semilla=99):
    """
    Genera un perfil de irradiancia solar horaria (W/m²) para un año.
    
    Modela la irradiancia en Colombia (zona ecuatorial):
    - Máximo al mediodía solar
    - Variación estacional según declinación solar
    - Nubosidad aleatoria (importante en trópico)
    - Sin generación nocturna
    """
    random.seed(semilla)
    irradiancia_horaria = []
    
    IRRADIANCIA_MAXIMA = 1000  # W/m² (constante solar en superficie con cielo despejado)
    
    for dia in range(365):
        # Declinación solar
        declinacion = 23.45 * math.sin(math.radians(360 * (284 + dia) / 365))
        declinacion_rad = math.radians(declinacion)
        latitud_rad = math.radians(LATITUD_GRADOS)
        
        # Ángulo horario de salida/puesta del sol
        cos_omega_s = -math.tan(latitud_rad) * math.tan(declinacion_rad)
        cos_omega_s = max(-1, min(1, cos_omega_s))
        omega_s = math.degrees(math.acos(cos_omega_s))  # grados
        horas_luz = 2 * omega_s / 15  # horas de luz solar
        
        # Hora solar del amanecer y atardecer
        hora_amanecer = 12 - horas_luz / 2
        hora_atardecer = 12 + horas_luz / 2
        
        # Factor de nubosidad diaria (trópico: más nubes en tarde)
        factor_nubes = random.triangular(0.5, 1.0, 0.85)
        
        for hora in range(24):
            hora_solar = hora + 0.5  # Centro de la hora
            
            if hora_solar <= hora_amanecer or hora_solar >= hora_atardecer:
                irradiancia = 0.0
            else:
                # Ángulo horario
                omega = math.radians(15 * (hora_solar - 12))
                
                # Coseno del ángulo de incidencia (panel inclinado = latitud)
                cos_theta = (math.sin(latitud_rad) * math.sin(declinacion_rad) +
                            math.cos(latitud_rad) * math.cos(declinacion_rad) * math.cos(omega))
                cos_theta = max(0, cos_theta)
                
                irradiancia_base = IRRADIANCIA_MAXIMA * cos_theta
                
                # Nubosidad horaria (más nublado en la tarde en Colombia)
                if hora >= 13:
                    factor_h = factor_nubes * random.triangular(0.6, 1.0, 0.75)
                else:
                    factor_h = factor_nubes * random.triangular(0.7, 1.0, 0.88)
                
                irradiancia = irradiancia_base * factor_h
                irradiancia = max(0, irradiancia)
            
            irradiancia_horaria.append(irradiancia)
    
    return irradiancia_horaria


# ─────────────────────────────────────────────────────────────────────────────
# SIMULACIÓN HORARIA DEL SISTEMA
# ─────────────────────────────────────────────────────────────────────────────

def simular_sistema(num_paneles, capacidad_bat_kwh, consumo_h, irradiancia_h):
    """
    Simula la operación hora a hora del sistema solar + batería durante un año.
    
    Estrategia de despacho (prioridad solar):
    1. La generación solar abastece primero la demanda local
    2. El exceso carga la batería (si tiene capacidad)
    3. Si la batería está llena, el exceso se vende a la red
    4. Si hay déficit, primero descarga la batería
    5. Si la batería está en SOC mínimo, compra de la red
    
    Retorna un diccionario con métricas anuales de desempeño.
    """
    # Parámetros del sistema
    potencia_pico_kw = num_paneles * PANEL_POTENCIA_W / 1000
    
    # Estado inicial de la batería (50% de SOC)
    soc = 0.5 if capacidad_bat_kwh > 0 else 0
    
    # Acumuladores anuales
    energia_solar_total = 0      # kWh generados por los paneles
    energia_consumida_total = 0  # kWh consumidos por el usuario
    energia_red_comprada = 0     # kWh comprados a la red
    energia_red_vendida = 0      # kWh vendidos a la red
    energia_bateria_cargada = 0  # kWh cargados en batería
    energia_bateria_descargada = 0  # kWh descargados de batería
    horas_autosuficiente = 0     # Horas sin comprar de la red
    
    for h in range(8760):
        irr = irradiancia_h[h]   # W/m²
        dem = consumo_h[h]       # kW demandado
        
        # 1. Generación fotovoltaica (kW)
        gen_pv = (irr / 1000) * potencia_pico_kw * INVERSOR_EFICIENCIA
        
        energia_solar_total += gen_pv
        energia_consumida_total += dem
        
        # Balance energético neto
        balance = gen_pv - dem  # kW (positivo = exceso, negativo = déficit)
        
        if capacidad_bat_kwh > 0:
            if balance >= 0:
                # Exceso de generación → cargar batería
                soc_max_carga = BAT_SOC_MAX
                max_carga_kw = min(balance,
                                   capacidad_bat_kwh * BAT_C_RATE_MAX,
                                   (soc_max_carga - soc) * capacidad_bat_kwh)
                max_carga_kw = max(0, max_carga_kw)
                
                energia_cargada = max_carga_kw * BAT_EFICIENCIA_CARGA
                soc += energia_cargada / capacidad_bat_kwh
                energia_bateria_cargada += energia_cargada
                
                # Exceso restante → vender a la red
                exceso_red = balance - max_carga_kw
                energia_red_vendida += exceso_red
                horas_autosuficiente += 1
                
            else:
                # Déficit → descargar batería
                deficit = abs(balance)
                max_descarga_kw = min(deficit,
                                      capacidad_bat_kwh * BAT_C_RATE_MAX,
                                      (soc - BAT_SOC_MIN) * capacidad_bat_kwh)
                max_descarga_kw = max(0, max_descarga_kw)
                
                energia_descargada = max_descarga_kw / BAT_EFICIENCIA_DESCARGA
                soc -= energia_descargada / capacidad_bat_kwh
                energia_bateria_descargada += max_descarga_kw
                
                # Déficit restante → comprar de la red
                deficit_restante = deficit - max_descarga_kw
                energia_red_comprada += deficit_restante
                
                if deficit_restante < 0.01:
                    horas_autosuficiente += 1
        else:
            # Sin batería
            if balance >= 0:
                energia_red_vendida += balance
                horas_autosuficiente += 1
            else:
                energia_red_comprada += abs(balance)
    
    # ── Métricas de desempeño ──
    fraccion_solar = 1 - (energia_red_comprada / energia_consumida_total)
    fraccion_solar = max(0, min(1, fraccion_solar))
    autosuficiencia = horas_autosuficiente / 8760
    co2_evitado_kg = (energia_consumida_total - energia_red_comprada) * EMISION_CO2_KG_KWH
    
    return {
        "energia_solar_kwh": energia_solar_total,
        "energia_consumida_kwh": energia_consumida_total,
        "energia_red_comprada_kwh": energia_red_comprada,
        "energia_red_vendida_kwh": energia_red_vendida,
        "fraccion_solar": fraccion_solar,
        "autosuficiencia_pct": autosuficiencia * 100,
        "co2_evitado_kg": co2_evitado_kg,
    }


# ─────────────────────────────────────────────────────────────────────────────
# ANÁLISIS ECONÓMICO (Valor Presente Neto del Costo)
# ─────────────────────────────────────────────────────────────────────────────

def calcular_costo_anual_equivalente(num_paneles, capacidad_bat_kwh, resultados_sim):
    """
    Calcula el Costo Anual Equivalente (CAE) del sistema usando el método
    del Factor de Recuperación del Capital (FRC).
    
    CAE = Inversión × FRC + Costos O&M anuales + Costos de energía de red
          - Ingresos por venta de excedentes
    
    El FRC convierte la inversión inicial en pagos anuales equivalentes,
    considerando la tasa de descuento y la vida útil de cada componente.
    """
    def frc(tasa, n_anos):
        """Factor de Recuperación del Capital"""
        if tasa == 0:
            return 1 / n_anos
        return (tasa * (1 + tasa)**n_anos) / ((1 + tasa)**n_anos - 1)
    
    # Costos de inversión
    costo_paneles = num_paneles * PANEL_COSTO_USD
    costo_baterias = capacidad_bat_kwh * BAT_COSTO_USD_KWH
    costo_inversor = INVERSOR_COSTO_USD
    costo_instalacion = (costo_paneles + costo_baterias) * 0.15  # 15% instalación
    
    # Costos anuales equivalentes por componente
    cae_paneles = costo_paneles * frc(TASA_DESC_ANUAL, PANEL_VIDA_ANOS)
    cae_baterias = costo_baterias * frc(TASA_DESC_ANUAL, BAT_VIDA_ANOS) if capacidad_bat_kwh > 0 else 0
    cae_inversor = costo_inversor * frc(TASA_DESC_ANUAL, INVERSOR_VIDA_ANOS)
    cae_instalacion = costo_instalacion * frc(TASA_DESC_ANUAL, HORIZONTE_ANOS)
    
    # Operación y mantenimiento (1% del costo de paneles anual)
    costo_oym = costo_paneles * 0.01
    
    # Costo anual de energía de la red
    costo_red = resultados_sim["energia_red_comprada_kwh"] * PRECIO_COMPRA_USD_KWH
    
    # Ingreso por venta de excedentes
    ingreso_venta = resultados_sim["energia_red_vendida_kwh"] * PRECIO_VENTA_USD_KWH
    
    # Costo Anual Equivalente total
    cae_total = (cae_paneles + cae_baterias + cae_inversor + cae_instalacion
                 + costo_oym + costo_red - ingreso_venta)
    
    # Costo sin sistema solar (línea base)
    cae_sin_solar = resultados_sim["energia_consumida_kwh"] * PRECIO_COMPRA_USD_KWH
    
    # Ahorro anual
    ahorro_anual = cae_sin_solar - cae_total
    
    # Inversión total
    inversion_total = costo_paneles + costo_baterias + costo_inversor + costo_instalacion
    
    # Período de retorno simple (payback)
    payback = inversion_total / ahorro_anual if ahorro_anual > 0 else float('inf')
    
    return {
        "inversion_total_usd": inversion_total,
        "cae_sistema_usd": cae_total,
        "costo_red_anual_usd": costo_red,
        "ingreso_venta_usd": ingreso_venta,
        "ahorro_anual_usd": ahorro_anual,
        "payback_anos": payback,
    }


# ─────────────────────────────────────────────────────────────────────────────
# OPTIMIZADOR PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def optimizar_sistema():
    """
    Itera sobre todas las combinaciones de paneles y baterías para encontrar
    la configuración que minimiza el Costo Anual Equivalente.
    """
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║     OPTIMIZADOR DE SISTEMA HÍBRIDO SOLAR-BATERÍA                ║")
    print("║     Ingeniería en Energía y Sostenibilidad                      ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    print("📍 Ubicación: Bucaramanga, Colombia (HSP = 5.2 h/día)")
    print("🏠 Usuario: Hogar familiar (~3,500 kWh/año)")
    print()
    
    # Generar perfiles horarios (una sola vez)
    print("⚙  Generando perfil de consumo horario (8,760 horas)...")
    consumo_h = generar_perfil_consumo()
    
    print("☀  Generando perfil de irradiancia solar horaria...")
    irradiancia_h = generar_perfil_irradiancia()
    
    consumo_anual = sum(consumo_h)
    print(f"\n📊 Consumo anual del usuario: {consumo_anual:.1f} kWh/año")
    print(f"   Demanda promedio: {consumo_anual/8760*1000:.0f} W")
    print(f"   Tarifa eléctrica: ${PRECIO_COMPRA_USD_KWH:.2f} USD/kWh")
    print(f"   Costo sin solar: ${consumo_anual * PRECIO_COMPRA_USD_KWH:.0f} USD/año")
    
    # Línea base (sin sistema solar)
    print("\n" + "─"*66)
    print("🔍 Iniciando optimización...")
    
    opciones_paneles = range(MIN_PANELES, MAX_PANELES + 1, PASO_PANELES)
    opciones_baterias = range(MIN_BAT_KWH, MAX_BAT_KWH + 1, PASO_BAT_KWH)
    
    total_combinaciones = len(list(opciones_paneles)) * len(list(opciones_baterias))
    print(f"   Evaluando {total_combinaciones} combinaciones...\n")
    
    resultados = []
    mejor_cae = float('inf')
    
    for num_paneles in opciones_paneles:
        for bat_kwh in opciones_baterias:
            # Simulación horaria
            sim = simular_sistema(num_paneles, bat_kwh, consumo_h, irradiancia_h)
            
            # Análisis económico
            econ = calcular_costo_anual_equivalente(num_paneles, bat_kwh, sim)
            
            resultado = {
                "paneles": num_paneles,
                "bateria_kwh": bat_kwh,
                "potencia_kw": num_paneles * PANEL_POTENCIA_W / 1000,
                **sim,
                **econ,
            }
            resultados.append(resultado)
            
            if econ["cae_sistema_usd"] < mejor_cae:
                mejor_cae = econ["cae_sistema_usd"]
    
    # Ordenar por CAE
    resultados.sort(key=lambda x: x["cae_sistema_usd"])
    
    return resultados, consumo_anual


# ─────────────────────────────────────────────────────────────────────────────
# PRESENTACIÓN DE RESULTADOS
# ─────────────────────────────────────────────────────────────────────────────

def presentar_resultados(resultados, consumo_anual):
    """Presenta los resultados de la optimización de forma clara."""
    
    optimo = resultados[0]
    
    print("═"*66)
    print("🏆  CONFIGURACIÓN ÓPTIMA ENCONTRADA")
    print("═"*66)
    print()
    print(f"  🔆 Paneles solares:    {optimo['paneles']} paneles × {PANEL_POTENCIA_W}W "
          f"= {optimo['potencia_kw']:.1f} kWp")
    print(f"  🔋 Batería:           {optimo['bateria_kwh']} kWh (LiFePO4)")
    print()
    print("─"*66)
    print("  DESEMPEÑO ENERGÉTICO ANUAL")
    print("─"*66)
    print(f"  ⚡ Consumo total:       {optimo['energia_consumida_kwh']:>8.1f} kWh/año")
    print(f"  ☀  Generación solar:    {optimo['energia_solar_kwh']:>8.1f} kWh/año")
    print(f"  🔌 Compra a la red:    {optimo['energia_red_comprada_kwh']:>8.1f} kWh/año")
    print(f"  📤 Venta a la red:     {optimo['energia_red_vendida_kwh']:>8.1f} kWh/año")
    print(f"  🌱 Fracción solar:     {optimo['fraccion_solar']*100:>8.1f}%")
    print(f"  🏠 Autosuficiencia:    {optimo['autosuficiencia_pct']:>8.1f}% de las horas")
    print(f"  🌍 CO₂ evitado:        {optimo['co2_evitado_kg']:>8.0f} kg/año")
    print()
    print("─"*66)
    print("  ANÁLISIS ECONÓMICO")
    print("─"*66)
    print(f"  💰 Inversión total:    ${optimo['inversion_total_usd']:>8,.0f} USD")
    print(f"  📉 CAE del sistema:    ${optimo['cae_sistema_usd']:>8,.0f} USD/año")
    print(f"  📈 CAE sin solar:      ${consumo_anual * PRECIO_COMPRA_USD_KWH:>8,.0f} USD/año")
    print(f"  💵 Ahorro anual:       ${optimo['ahorro_anual_usd']:>8,.0f} USD/año")
    print(f"  ⏱  Payback:            {optimo['payback_anos']:>8.1f} años")
    print()
    print("═"*66)
    
    # Top 5 configuraciones
    print("\n📋  TOP 5 CONFIGURACIONES POR COSTO ANUAL EQUIVALENTE")
    print("─"*66)
    print(f"  {'#':<3} {'Paneles':<8} {'Bat(kWh)':<10} {'F.Solar%':<10} "
          f"{'CAE(USD/año)':<14} {'Payback':<8}")
    print("  " + "─"*62)
    
    for i, r in enumerate(resultados[:5]):
        marca = "◀ ÓPTIMO" if i == 0 else ""
        print(f"  {i+1:<3} {r['paneles']:<8} {r['bateria_kwh']:<10} "
              f"{r['fraccion_solar']*100:<10.1f} "
              f"${r['cae_sistema_usd']:<13,.0f} "
              f"{r['payback_anos']:.1f}a {marca}")
    
    print()
    print("─"*66)
    print("💡 RECOMENDACIÓN DE INGENIERÍA")
    print("─"*66)
    
    # Análisis de sensibilidad simple
    fraccion = optimo['fraccion_solar']
    if fraccion >= 0.9:
        print("  ✅ El sistema alcanza alta autosuficiencia (>90% solar).")
        print("     Ideal para zonas con interrupciones frecuentes de red.")
    elif fraccion >= 0.7:
        print("  ✅ Balance óptimo entre inversión y autosuficiencia.")
        print("     Se recomienda esta configuración como punto de partida.")
    else:
        print("  ⚠  La fracción solar es moderada. Considere aumentar paneles")
        print("     si el objetivo principal es la resiliencia energética.")
    
    payback = optimo['payback_anos']
    if payback <= 7:
        print(f"  ✅ Payback de {payback:.1f} años: excelente retorno de inversión.")
    elif payback <= 12:
        print(f"  ✅ Payback de {payback:.1f} años: retorno de inversión aceptable.")
    else:
        print(f"  ⚠  Payback de {payback:.1f} años: evalúe subsidios o incentivos fiscales.")
    
    if optimo['bateria_kwh'] == 0:
        print("  💡 Sin batería es óptimo económicamente. Si se requiere")
        print("     resiliencia ante apagones, agregar al menos 10 kWh.")
    
    co2_equiv_arboles = optimo['co2_evitado_kg'] / 21  # ~21 kg CO₂/árbol/año
    print(f"  🌳 El CO₂ evitado equivale a plantar {co2_equiv_arboles:.0f} árboles/año.")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# ANÁLISIS DE SENSIBILIDAD
# ─────────────────────────────────────────────────────────────────────────────

def analisis_sensibilidad(optimo, consumo_h, irradiancia_h):
    """
    Analiza cómo cambia la decisión óptima ante variaciones en:
    - Precio de la electricidad (±30%)
    - Costo de los paneles (±20%)
    - Costo de las baterías (±30%)
    """
    print("─"*66)
    print("📊  ANÁLISIS DE SENSIBILIDAD")
    print("─"*66)
    
    global PRECIO_COMPRA_USD_KWH, PANEL_COSTO_USD, BAT_COSTO_USD_KWH
    
    base = {
        "precio_red": PRECIO_COMPRA_USD_KWH,
        "costo_panel": PANEL_COSTO_USD,
        "costo_bat": BAT_COSTO_USD_KWH,
    }
    
    escenarios = [
        ("Tarifa eléctrica +30%",     {"precio_red": base["precio_red"] * 1.3}),
        ("Tarifa eléctrica -30%",     {"precio_red": base["precio_red"] * 0.7}),
        ("Paneles -20% (economía escala)", {"costo_panel": base["costo_panel"] * 0.8}),
        ("Baterías -30% (tendencia)",  {"costo_bat": base["costo_bat"] * 0.7}),
    ]
    
    print(f"  {'Escenario':<35} {'CAE(USD)':<12} {'Payback':<8}")
    print("  " + "─"*58)
    
    n_p = optimo["paneles"]
    n_b = optimo["bateria_kwh"]
    
    for nombre, cambio in escenarios:
        # Aplicar cambio temporal
        precio_orig = PRECIO_COMPRA_USD_KWH
        panel_orig = PANEL_COSTO_USD
        bat_orig = BAT_COSTO_USD_KWH
        
        if "precio_red" in cambio:
            PRECIO_COMPRA_USD_KWH = cambio["precio_red"]
        if "costo_panel" in cambio:
            PANEL_COSTO_USD = cambio["costo_panel"]
        if "costo_bat" in cambio:
            BAT_COSTO_USD_KWH = cambio["costo_bat"]
        
        sim = simular_sistema(n_p, n_b, consumo_h, irradiancia_h)
        econ = calcular_costo_anual_equivalente(n_p, n_b, sim)
        
        print(f"  {nombre:<35} ${econ['cae_sistema_usd']:<11,.0f} {econ['payback_anos']:.1f} años")
        
        # Restaurar valores
        PRECIO_COMPRA_USD_KWH = precio_orig
        PANEL_COSTO_USD = panel_orig
        BAT_COSTO_USD_KWH = bat_orig
    
    print()


# ─────────────────────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    
    # 1. Ejecutar optimización
    resultados, consumo_anual = optimizar_sistema()
    
    # 2. Presentar resultados
    presentar_resultados(resultados, consumo_anual)
    
    # 3. Análisis de sensibilidad con la configuración óptima
    optimo = resultados[0]
    consumo_h = generar_perfil_consumo()
    irradiancia_h = generar_perfil_irradiancia()
    analisis_sensibilidad(optimo, consumo_h, irradiancia_h)
    
    print("═"*66)
    print("✅  Análisis completado.")
    print("   Para personalizar, modifique los parámetros en la sección")
    print("   'PARÁMETROS DEL SISTEMA' al inicio del archivo.")
    print("═"*66)
