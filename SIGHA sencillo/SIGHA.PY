import sqlite3

# 1. Función para preparar la base de datos
def iniciar_db():
    conexion = sqlite3.connect('sigha_pro.db')
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            direccion TEXT, 
            estrato INTEGER, 
            consumo REAL, 
            total REAL
        )
    ''')
    conexion.commit()
    conexion.close()

# 2. Función para buscar historial
def buscar_historial(direc):
    conexion = sqlite3.connect('sigha_pro.db')
    cursor = conexion.cursor()
    cursor.execute('SELECT estrato, consumo FROM registros WHERE direccion = ? ORDER BY id DESC LIMIT 1', (direc.lower(),))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado

# 3. Función para REGISTRAR 
def registrar_factura():
    print("\n--- NUEVO REGISTRO DE FACTURA ---")
    direccion = input("Dirección del predio: ").strip()
    
    historial = buscar_historial(direccion)
    consumo_anterior = 0
    
    if historial:
        estrato = historial[0]
        consumo_anterior = historial[1]
        print(f"✅ Predio reconocido. Estrato automático: {estrato}")
    else:
        estrato = int(input("Es un predio nuevo. Ingresa el estrato (1, 2 o 3): "))

    consumo_actual = float(input("¿Cuántos m3 consumió este mes?: "))
    precio_m3 = float(input("¿Precio del m3?: $"))
    
    subsidio = {1: 0.50, 2: 0.25, 3: 0.10}.get(estrato, 0)
    total_bruto = consumo_actual * precio_m3
    ahorro = total_bruto * subsidio
    pago_neto = total_bruto - ahorro

    # Lógica de Fuga
    mensaje_fuga = ""
    if consumo_anterior > 0:
        if consumo_actual > (consumo_anterior * 1.30):
            mensaje_fuga = "\n⚠️ ¡ALERTA! Posible fuga detectada (aumento > 30%).\n   Se necesita revisar las instalaciones."

    # Mensaje Ambiental
    if consumo_actual <= 15:
        conciencia = "🌱 CONSUMO BAJO.¡HEROE DEL AGUA! Tu ahorro es ejemplar."
    elif consumo_actual <= 30:
        conciencia = "💧 CONSUMO RESPONSABLE. Cada gota cuenta."
    else:
        conciencia = "⚠️ CONSUMO EXCESIVO. El planeta te pide ahorrar más."

    # Guardar
    conexion = sqlite3.connect('sigha_pro.db')
    cursor = conexion.cursor()
    cursor.execute('INSERT INTO registros (direccion, estrato, consumo, total) VALUES (?, ?, ?, ?)', 
                   (direccion.lower(), estrato, consumo_actual, pago_neto))
    conexion.commit()
    conexion.close()

    # Mostrar Factura
    factura = f"""
=============================================
         FACTURA DE SERVICIO SIGHA
=============================================
 DIRECCIÓN: {direccion.upper()}
 ESTRATO:   {estrato}
 CONSUMO:   {consumo_actual} m3 (Anterior: {consumo_anterior}m3)
---------------------------------------------
 VALOR BRUTO:    ${total_bruto:,.0f}
 SUBSIDIO:      -${ahorro:,.0f}
 TOTAL A PAGAR:  ${pago_neto:,.0f}
---------------------------------------------{mensaje_fuga}

 MENSAJE AMBIENTAL:
 {conciencia}
=============================================
    """
    print(factura)
    input("Presiona ENTER para volver al menú...")

# 4. MENÚ PRINCIPAL (El corazón del programa)
def menu():
    iniciar_db()
    
    while True: # Esto hace que el programa se "reinicie" solo
        print("\n" + "="*30)
        print("      MENÚ PRINCIPAL SIGHA")
        print("="*30)
        print("1. Registrar nueva factura")
        print("2. Salir del programa")
        
        opcion = input("\nSelecciona una opción (1 o 2): ")

        if opcion == "1":
            registrar_factura()
        elif opcion == "2":
            print("\nGracias por usar SIGHA. ¡Cierra el grifo! 💧")
            break # Rompe el bucle y cierra el programa
        else:
            print("\n❌ Opción no válida. Intenta de nuevo.")

# Arrancar el sistema
if __name__ == "__main__":
    menu()