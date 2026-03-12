import sqlite3

def inicializar_db():
    conexion = sqlite3.connect('sigha_data.db')
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS consumos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            direccion TEXT,
            estrato INTEGER,
            consumo REAL,
            total_neto REAL,
            alerta_fuga TEXT
        )
    ''')
    conexion.commit()
    conexion.close()
    
def obtener_todos_los_predios():
    conexion = sqlite3.connect('sigha_data.db')
    cursor = conexion.cursor()
    # Seleccionamos direcciones únicas y su estrato más reciente
    cursor.execute('''
        SELECT direccion, estrato, COUNT(id) as visitas 
        FROM consumos 
        GROUP BY direccion 
        ORDER BY direccion ASC
    ''')
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

def guardar_registro_db(datos):
    conexion = sqlite3.connect('sigha_data.db')
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT INTO consumos (fecha, direccion, estrato, consumo, total_neto, alerta_fuga)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (datos['Fecha'], datos['Direccion'], datos['Estrato'], 
          datos['Consumo'], datos['Total_Neto'], datos['Alerta_Fuga']))
    conexion.commit()
    conexion.close()

def buscar_datos_predio(direccion):
    conexion = sqlite3.connect('sigha_data.db')
    cursor = conexion.cursor()
    cursor.execute('SELECT estrato, consumo FROM consumos WHERE direccion = ? ORDER BY id DESC LIMIT 1', (direccion.lower(),))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado if resultado else (None, None)

def obtener_historial_completo(direccion):
    conexion = sqlite3.connect('sigha_data.db')
    cursor = conexion.cursor()
    # Usamos LOWER(?) para que no importe si escribes Calle 10 o calle 10
    cursor.execute('''
        SELECT fecha, consumo, total_neto, alerta_fuga 
        FROM consumos 
        WHERE LOWER(direccion) = LOWER(?) 
        ORDER BY id DESC
    ''', (direccion.strip(),))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados