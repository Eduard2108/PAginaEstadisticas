from flask import Flask, render_template, request, redirect, url_for, session, make_response
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from reportlab.pdfgen import canvas


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')

def es_numero(n):
    try:
        float(n)
        return True
    except ValueError:
        return False
    
@app.route('/GuardarBarcelona', methods=['POST'])
def guardarBarcelona():
    if not os.path.exists('datos_barcelona.json'):
        with open('datos_barcelona.json', 'w') as f:
            json.dump([], f)
    id_jugador = request.form['nombrejugador']
    goles = request.form['goles']
    asistencias = request.form['asistencias']
    perdidos = request.form['perdidos']
    ganados = request.form['ganados']
    empatados = request.form['empatados']
    remates = request.form['remates']
    tarjetas_rojas = request.form['tarjetasrojas']
    tarjetas_amarillas = request.form['tarjetasamarillas']
    datos = [goles, asistencias, perdidos, ganados, empatados, remates, tarjetas_rojas, tarjetas_amarillas]
    if not all(es_numero(dato) for dato in datos):
        return render_template('Barcelona.html')
    
    try:
        total_partidos = int(perdidos) + int(ganados) + int(empatados)
        probabilidad_ganar = round(int(ganados) / total_partidos, 2) *100
        porcen_goles = round(int(goles) / total_partidos, 2) 
    except ZeroDivisionError:
        return 'no se puede realizar divisiones para cero'
    
    jugador = {
        "ID Jugador": id_jugador,
        "Asistencias": asistencias,
        "Goles": goles,
        "Partidos perdidos": perdidos,
        "Partidos ganados": ganados,
        "Partidos empatados": empatados,
        "Remates al arco": remates,
        "Tarjetas Amarillas": tarjetas_amarillas,
        "Tarjetas Rojas": tarjetas_rojas,
        "Total de partidos": total_partidos,
        "Porcentaje de goles por partido": porcen_goles,
        "Probabilidad de ganar": probabilidad_ganar
    }
    with open('datos_barcelona.json', 'r') as f:
        datos = json.load(f)
    datos.append(jugador)
    with open('datos_barcelona.json', 'w') as f:
        json.dump(datos, f)
    return render_template('Barcelona.html')

@app.route('/mostrarbarcelona')
def mostrarBarcelona():
    try:
        with open('datos_barcelona.json', 'r') as f:
            datos = json.load(f)
            return render_template('EstadisticasBarcelona.html', datos=datos)
    except FileNotFoundError:
        return 'Aun no ingresa datos'

@app.route('/graficosBarcelona')
def graficosBarcelona():
    df = pd.read_json('datos_barcelona.json')
    df['Goles'] = df['Goles'].astype(int)
    df['Asistencias'] = df['Asistencias'].astype(int)
    df['Partidos perdidos'] = df['Partidos perdidos'].astype(int)
    df['Partidos ganados'] = df['Partidos ganados'].astype(int)
    df['Partidos empatados'] = df['Partidos empatados'].astype(int)
    df['Tarjetas Amarillas'] = df['Tarjetas Amarillas'].astype(int)
    df['Tarjetas Rojas'] = df['Tarjetas Rojas'].astype(int)
    df['Remates al arco'] = df['Remates al arco'].astype(int)
    grouped = df.groupby('ID Jugador').sum()

    graficos_jugadores = []
    for jugador, stats in grouped.iterrows():
        fig, ax = plt.subplots()
        labels = ['Goles', 'Asistencias', 'Partidos perdidos', 'Partidos ganados', 'Partidos empatados','Tarjetas Amarillas','Tarjetas Rojas','Remates al arco']
        sizes = [stats['Goles'], stats['Asistencias'], stats['Partidos perdidos'], stats['Partidos ganados'], stats['Partidos empatados'], stats['Tarjetas Amarillas'],stats['Tarjetas Rojas'],stats['Remates al arco']]
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        plt.axis('equal')

        # Convertir el gráfico a formato base64
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        graficos_jugadores.append({
            'nombre_jugador': jugador,
            'grafico_base64': img_base64,
        })

    return render_template('GraficoBarcelona.html', graficos_jugadores=graficos_jugadores)

@app.route('/descargar_tabla_jugadores')
def pdf_barcelona():
    with open('datos_barcelona.json', 'r') as f:
        datos = json.load(f)

    # Crear un objeto PDF con reportlab
    response = make_response()
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=jugadores.pdf'

    # Crear el PDF con reportlab
    pdf_buffer = create_pdf_barcelona_from_json(datos)
    response.set_data(pdf_buffer.getvalue())

    return response

def create_pdf_barcelona_from_json(datos):
    from io import BytesIO

    buffer = BytesIO()

    # Crear un objeto PDF con reportlab
    pdf = canvas.Canvas(buffer)

    # Agregar datos al PDF
    for jugador in datos:
        pdf.drawString(100, 700, f"ID Jugador: {jugador['ID Jugador']}")
        pdf.drawString(100, 680, f"Goles: {jugador['Goles']}")
        pdf.drawString(100, 660, f"Asistencias: {jugador['Asistencias']}")
        pdf.drawString(100, 640, f"Partidos perdidos: {jugador['Partidos perdidos']}")
        pdf.drawString(100, 620, f"Partidos ganados {jugador['Partidos ganados']}")
        pdf.drawString(100, 600, f"Partidos empetados {jugador['Partidos empatados']}")
        pdf.drawString(100, 580, f"Remates al arco {jugador['Remates al arco']}")
        pdf.drawString(100, 560, f"Tarjetas Amarillas {jugador['Tarjetas Amarillas']}")
        pdf.drawString(100, 540, f"Tarjetas Rojas {jugador['Tarjetas Rojas']}")
        pdf.drawString(100, 520, f"Total de partidos {jugador['Total de partidos']}")
        pdf.drawString(100, 500, f"Porcentaje de goles por partido {jugador['Porcentaje de goles por partido']}")
        pdf.drawString(100, 480, f"Probabilidad de ganar {jugador['Probabilidad de ganar']}")
        # Agregar un salto de página para el próximo jugador
        pdf.showPage()

    pdf.save()
    buffer.seek(0)

    return buffer

def es_numero(n):
    try:
        float(n)
        return True
    except ValueError:
        return False
    
@app.route('/GuardarManchesterCity', methods=['POST'])
def guardarManchesterCity():
    if not os.path.exists('datos_manchester_city.json'):
        with open('datos_manchester_city.json', 'w') as f:
            json.dump([], f)
    id_jugador = request.form['nombrejugador']
    goles = request.form['goles']
    asistencias = request.form['asistencias']
    perdidos = request.form['perdidos']
    ganados = request.form['ganados']
    empatados = request.form['empatados']
    remates = request.form['remates']
    tarjetas_rojas = request.form['tarjetasrojas']
    tarjetas_amarillas = request.form['tarjetasamarillas']
    datos = [goles, asistencias, perdidos, ganados, empatados, remates, tarjetas_rojas, tarjetas_amarillas]
    if not all(es_numero(dato) for dato in datos):
        return render_template('ManchesterCity.html')
    
    try:
        total_partidos = int(perdidos) + int(ganados) + int(empatados)
        probabilidad_ganar = round(int(ganados) / total_partidos, 2) *100
        porcen_goles = round(int(goles) / total_partidos, 2) 
    except ZeroDivisionError:
        return 'no se puede realizar divisiones para cero'

    jugador = {
        "ID Jugador": id_jugador,
        "Goles": goles,
        "Asistencias": asistencias,
        "Partidos perdidos": perdidos,
        "Partidos ganados": ganados,
        "Partidos empatados": empatados,
        "Remates al arco": remates,
        "Tarjetas Amarillas": tarjetas_amarillas,
        "Tarjetas Rojas": tarjetas_rojas,
        "Total de partidos": total_partidos,
        "Porcentaje de goles por partido": porcen_goles,
        "Probabilidad de ganar": probabilidad_ganar
    }
    with open('datos_manchester_city.json', 'r') as f:
        datos = json.load(f)
    datos.append(jugador)
    with open('datos_manchester_city.json', 'w') as f:
        json.dump(datos, f)
    return render_template('ManchesterCity.html')

@app.route('/graficoManchester')
def graficosManchester():
    df = pd.read_json('datos_manchester_city.json')
    df['Goles'] = df['Goles'].astype(int)
    df['Asistencias'] = df['Asistencias'].astype(int)
    df['Partidos perdidos'] = df['Partidos perdidos'].astype(int)
    df['Partidos ganados'] = df['Partidos ganados'].astype(int)
    df['Partidos empatados'] = df['Partidos empatados'].astype(int)
    df['Tarjetas Amarillas'] = df['Tarjetas Amarillas'].astype(int)
    df['Tarjetas Rojas'] = df['Tarjetas Rojas'].astype(int)
    df['Remates al arco'] = df['Remates al arco'].astype(int)
    grouped = df.groupby('ID Jugador').sum()

    graficos_jugadores = []
    for jugador, stats in grouped.iterrows():
        fig, ax = plt.subplots()
        labels = ['Goles', 'Asistencias', 'Partidos perdidos', 'Partidos ganados', 'Partidos empatados','Tarjetas Amarillas','Tarjetas Rojas','Remates al arco']
        sizes = [stats['Goles'], stats['Asistencias'], stats['Partidos perdidos'], stats['Partidos ganados'], stats['Partidos empatados'], stats['Tarjetas Amarillas'],stats['Tarjetas Rojas'],stats['Remates al arco']]
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        plt.axis('equal')

        # Convertir el gráfico a formato base64
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        graficos_jugadores.append({
            'nombre_jugador': jugador,
            'grafico_base64': img_base64,
        })

    return render_template('GraficoManchesterCity.html', graficos_jugadores=graficos_jugadores)

@app.route('/descargar_tabla_jugadores_manchester')
def pdf_manchester():
    with open('datos_manchester_city.json', 'r') as f:
        datos = json.load(f)

    # Crear un objeto PDF con reportlab
    response = make_response()
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=jugadores.pdf'

    # Crear el PDF con reportlab
    pdf_buffer = create_pdf_manchester_from_json(datos)
    response.set_data(pdf_buffer.getvalue())

    return response

def create_pdf_manchester_from_json(datos):
    from io import BytesIO

    buffer = BytesIO()

    # Crear un objeto PDF con reportlab
    pdf = canvas.Canvas(buffer)

    # Agregar datos al PDF
    for jugador in datos:
        pdf.drawString(100, 700, f"ID Jugador: {jugador['ID Jugador']}")
        pdf.drawString(100, 680, f"Goles: {jugador['Goles']}")
        pdf.drawString(100, 660, f"Asistencias: {jugador['Asistencias']}")
        pdf.drawString(100, 640, f"Partidos perdidos: {jugador['Partidos perdidos']}")
        pdf.drawString(100, 620, f"Partidos ganados {jugador['Partidos ganados']}")
        pdf.drawString(100, 600, f"Partidos empetados {jugador['Partidos empatados']}")
        pdf.drawString(100, 580, f"Remates al arco {jugador['Remates al arco']}")
        pdf.drawString(100, 560, f"Tarjetas Amarillas {jugador['Tarjetas Amarillas']}")
        pdf.drawString(100, 540, f"Tarjetas Rojas {jugador['Tarjetas Rojas']}")
        pdf.drawString(100, 520, f"Total de partidos {jugador['Total de partidos']}")
        pdf.drawString(100, 500, f"Porcentaje de goles por partido {jugador['Porcentaje de goles por partido']}")
        pdf.drawString(100, 480, f"Probabilidad de ganar {jugador['Probabilidad de ganar']}")
        # Agregar un salto de página para el próximo jugador
        pdf.showPage()

    pdf.save()
    buffer.seek(0)

    return buffer
@app.route('/mostrarmanchestercity')
def mostrarManchestercity():
    try:
        with open('datos_manchester_city.json', 'r') as f:
            datos = json.load(f)
            return render_template('EstadisticasManchesterCity.html', datos=datos)
    except FileNotFoundError:
        return 'Aun no ingresa datos'

def es_numero(n):
    try:
        float(n)
        return True
    except ValueError:
        return False
    
@app.route('/GuardarRealMadrid', methods=['POST'])
def guardarRealMadrid():
    if not os.path.exists('datos_real_madrid.json'):
        with open('datos_real_madrid.json', 'w') as f:
            json.dump([], f)
    id_jugador = request.form['nombrejugador']
    goles = request.form['goles']
    asistencias = request.form['asistencias']
    perdidos = request.form['perdidos']
    ganados = request.form['ganados']
    empatados = request.form['empatados']
    remates = request.form['remates']
    tarjetas_rojas = request.form['tarjetasrojas']
    tarjetas_amarillas = request.form['tarjetasamarillas']
    datos = [goles, asistencias, perdidos, ganados, empatados, remates, tarjetas_rojas, tarjetas_amarillas]
    if not all(es_numero(dato) for dato in datos):
        return render_template('RealMadrid.html')
    try:
        total_partidos = int(perdidos) + int(ganados) + int(empatados)
        probabilidad_ganar = round(int(ganados) / total_partidos, 2) *100
        porcen_goles = round(int(goles) / total_partidos, 2) 
    except ZeroDivisionError:
        return 'no se puede realizar divisiones para cero'
    
    jugador = {
        "ID Jugador": id_jugador,
        "Goles": goles,
        "Asistencias": asistencias,
        "Partidos perdidos": perdidos,
        "Partidos ganados": ganados,
        "Partidos empatados": empatados,
        "Remates al arco": remates,
        "Tarjetas Amarillas": tarjetas_amarillas,
        "Tarjetas Rojas": tarjetas_rojas,
        "Total de partidos": total_partidos,
        "Porcentaje de goles por partido": porcen_goles,
        "Probabilidad de ganar": probabilidad_ganar
    }
    with open('datos_real_madrid.json', 'r') as f:
        datos = json.load(f)
    datos.append(jugador)
    with open('datos_real_madrid.json', 'w') as f:
        json.dump(datos, f)
    return render_template('RealMadrid.html')

@app.route('/graficoRealMadrid')
def graficosRealMadrid():
    df = pd.read_json('datos_real_madrid.json')
    df['Goles'] = df['Goles'].astype(int)
    df['Asistencias'] = df['Asistencias'].astype(int)
    df['Partidos perdidos'] = df['Partidos perdidos'].astype(int)
    df['Partidos ganados'] = df['Partidos ganados'].astype(int)
    df['Partidos empatados'] = df['Partidos empatados'].astype(int)
    df['Tarjetas Amarillas'] = df['Tarjetas Amarillas'].astype(int)
    df['Tarjetas Rojas'] = df['Tarjetas Rojas'].astype(int)
    df['Remates al arco'] = df['Remates al arco'].astype(int)
    grouped = df.groupby('ID Jugador').sum()

    graficos_jugadores = []
    for jugador, stats in grouped.iterrows():
        fig, ax = plt.subplots()
        labels = ['Goles', 'Asistencias', 'Partidos perdidos', 'Partidos ganados', 'Partidos empatados','Tarjetas Amarillas','Tarjetas Rojas','Remates al arco']
        sizes = [stats['Goles'], stats['Asistencias'], stats['Partidos perdidos'], stats['Partidos ganados'], stats['Partidos empatados'], stats['Tarjetas Amarillas'],stats['Tarjetas Rojas'],stats['Remates al arco']]
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        plt.axis('equal')

        # Convertir el gráfico a formato base64
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        graficos_jugadores.append({
            'nombre_jugador': jugador,
            'grafico_base64': img_base64,
        })

    return render_template('GraficoRealMadrid.html', graficos_jugadores=graficos_jugadores)

@app.route('/descargar_tabla_jugadores_real_madrid')
def pdf_real_madrid():
    with open('datos_barcelona.json', 'r') as f:
        datos = json.load(f)

    # Crear un objeto PDF con reportlab
    response = make_response()
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=jugadores.pdf'

    # Crear el PDF con reportlab
    pdf_buffer = create_pdf_real_madrid_from_json(datos)
    response.set_data(pdf_buffer.getvalue())

    return response

def create_pdf_real_madrid_from_json(datos):
    from io import BytesIO

    buffer = BytesIO()

    # Crear un objeto PDF con reportlab
    pdf = canvas.Canvas(buffer)

    # Agregar datos al PDF
    for jugador in datos:
        pdf.drawString(100, 700, f"ID Jugador: {jugador['ID Jugador']}")
        pdf.drawString(100, 680, f"Goles: {jugador['Goles']}")
        pdf.drawString(100, 660, f"Asistencias: {jugador['Asistencias']}")
        pdf.drawString(100, 640, f"Partidos perdidos: {jugador['Partidos perdidos']}")
        pdf.drawString(100, 620, f"Partidos ganados {jugador['Partidos ganados']}")
        pdf.drawString(100, 600, f"Partidos empetados {jugador['Partidos empatados']}")
        pdf.drawString(100, 580, f"Remates al arco {jugador['Remates al arco']}")
        pdf.drawString(100, 560, f"Tarjetas Amarillas {jugador['Tarjetas Amarillas']}")
        pdf.drawString(100, 540, f"Tarjetas Rojas {jugador['Tarjetas Rojas']}")
        pdf.drawString(100, 520, f"Total de partidos {jugador['Total de partidos']}")
        pdf.drawString(100, 500, f"Porcentaje de goles por partido {jugador['Porcentaje de goles por partido']}")
        pdf.drawString(100, 480, f"Probabilidad de ganar {jugador['Probabilidad de ganar']}")
        # Agregar un salto de página para el próximo jugador
        pdf.showPage()

    pdf.save()
    buffer.seek(0)

    return buffer

@app.route('/mostrarRealmadrid')
def mostrarRealMadrid():
    try:
        with open('datos_real_madrid.json', 'r') as f:
            datos = json.load(f)
            return render_template('EstadisticasRealMadrid.html', datos=datos)
    except FileNotFoundError:
        return 'Aun no ingresa datos'

@app.route('/login')
def login():
    return render_template('Login.html')

@app.route('/ver_plantilla')
def ver_plantilla():
    if 'usuario_iniciado' in session:
        return render_template('ver_plantilla.html')
    else:
        return redirect(url_for('login'))

@app.route('/tabla_estadisticas')
def TablaEstadisticas():
    if 'usuario_iniciado' in session:
        return render_template('tabla_estadisticas.html')
    else:
        return redirect(url_for('login'))

#Login cuando de sobre iniciar sesion
@app.route('/logout')
def logout():
    session.pop('usuario_iniciado', None)
    return redirect(url_for('home'))

#Doy clic sobre el boton iniciar sesion y me lleva a la pagina de los clubes
@app.route('/clubes')  
def clubes():
    return render_template('Clubes.html')

#LLamar a la plantilla de los jugadores de Barcelona
@app.route('/barcelona')  
def club_barcelona():
    return render_template('Barcelona.html')

#Regresa a la Clubes
@app.route('/regresarbarcelona')  
def regresar_barcelona():
    return render_template('Clubes.html')

#Llama a la plantilla de jugadores deL ManchesterCity
@app.route('/manchestercity')  
def club_manchestercity():
    return render_template('ManchesterCity.html')

#Regresa a la Clubes
@app.route('/regresarmanchestercity')  
def regresar_manchestercity():
    return render_template('Clubes.html')

#llama a la plantilla de los jugadores de RealMadrid
@app.route('/realmadrid')  
def club_realmadrid():
    return render_template('RealMadrid.html')

#Regresa a la Clubes
@app.route('/regresarrealmadrid')  
def regresar_realmadrid():
    return render_template('Clubes.html')



if __name__ == '__main__':
    app.run(debug=True)
