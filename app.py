import csv
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, time, date
from sqlalchemy.orm import relationship

#Cargamos variables de entorno
load_dotenv()
#Llama a flask como app
app = Flask(__name__)
#ruta de la base de datos para que SQLAlchemy pueda conectarse
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///consultorio.db"
app.secret_key = os.getenv('SECRET_KEY')

#Nos permite crear consultas en SQL con SQLAlchemy
db = SQLAlchemy(app)

#Aca creamos la base de datos de los pacientes, usando clases como tablas
class Paciente(db.Model):
    __tablename__ = 'pacientes'  
    
    paciente_id = db.Column(db.Integer, primary_key=True)
    medico = db.Column(db.Text, nullable=True)
    historia_clinica = db.Column(db.Text, nullable=True)
    nombre_paciente = db.Column(db.Text, nullable=False)
    apellido = db.Column(db.Text, nullable=False)
    dni = db.Column(db.Text, nullable=True, unique=True)
    sexo = db.Column(db.Text, nullable=True)
    mail = db.Column(db.Text, nullable=True)
    telefono = db.Column(db.Text, nullable=True)
    telefono_celular = db.Column(db.Text, nullable=True)
    nacionalidad = db.Column(db.Text, nullable=True)
    domicilio = db.Column(db.Text, nullable=True)
    fecha_nacimiento = db.Column(db.Text, nullable=True)
    ocupacion = db.Column(db.Text, nullable=True)
    obra_social_1 = db.Column(db.Text, nullable=True)
    num_afiliado_1 = db.Column(db.Text, nullable=True)
    obra_social_2 = db.Column(db.Text, nullable=True)
    num_afiliado_2 = db.Column(db.Text, nullable=True)

    # Esta funcion inicializa la base de datos
def init_db():
    with app.app_context():
        db.create_all()
        # db.drop_all() 

#RUTAS

# Esta ruta es para subir un archivo csv
#@app.route('/subir_csv', methods=['GET'])
#def subir_archivo():
#    # ruta_csv = 'ruta del archivo csv'
#    try:
#        with open(ruta_csv, 'r', encoding='utf-8') as archivo:
#            csv_reader = csv.DictReader(archivo)
#            for fila in csv_reader:
#                paciente = Paciente(
#                    nombre_paciente=fila.get('nombre'),
#                    apellido=fila.get('apellido'),
#                    dni=fila.get('dni'),
#                    # Asigna otros campos
#                )
#                db.session.add(paciente)
#            
#            db.session.commit()
#            return "Pacientes cargados exitosamente."
#    except Exception as e:
#        db.session.rollback()
#        return f"Ocurrió un error: {e}"



# @app.route se utiliza para mapear rutas, esta lo que hace es mapear al index.html cuando se esta en la pagina principal
@app.route('/')
def home():
    # hacemos un getter para obtener los resultados de la busqueda de pacientes
    return render_template('index.html', resultados_busqueda=[], mensaje=None)

#ruta para el input de busqueda de datos del paciente
@app.route('/buscar_paciente', methods=['POST'])
def buscar_paciente():
    busqueda = request.form.get('busqueda')   # obtenemos los datos de la busqueda, del input del html

    # Query para obtener los pacientes que coincidan con la busqueda
    pacientes = Paciente.query.filter(
            (Paciente.nombre_paciente.ilike(f"%{busqueda}%")) |
            (Paciente.apellido.ilike(f"%{busqueda}%")) |
            (Paciente.dni.ilike(f"%{busqueda}%")) |
            (Paciente.mail.ilike(f"%{busqueda}%")) |
            (Paciente.telefono.ilike(f"%{busqueda}%")) |
            (Paciente.domicilio.ilike(f"%{busqueda}%")) |
            (Paciente.ocupacion.ilike(f"%{busqueda}%"))
        ).all()
    

    resultados = []
    for paciente in pacientes:
            # Obtener el turno más reciente, si es que existe
        turno = Turno.query.filter_by(nombre_apellido = paciente.apellido).order_by(Turno.fecha.desc()).first()
        obras_sociales = []
        if paciente.obra_social_1:
            obras_sociales.append({'nombre': paciente.obra_social_1, 'num_afiliado': paciente.num_afiliado_1})
        if paciente.obra_social_2:
            obras_sociales.append({'nombre': paciente.obra_social_2, 'num_afiliado': paciente.num_afiliado_2})

    #Lista con los resultados de la busqueda para mostrarlos en la página
        resultado = {
            'medico': paciente.medico,
            'historia_clinica': paciente.historia_clinica,
            'nombre': paciente.nombre_paciente,
            'apellido': paciente.apellido,
            'dni': paciente.dni,
            'sexo': paciente.sexo,
            'mail': paciente.mail,
            'telefono': paciente.telefono,
            'telefono_celular': paciente.telefono_celular,
            'nacionalidad': paciente.nacionalidad,
            'domicilio': paciente.domicilio,
            'fecha_nacimiento': paciente.fecha_nacimiento.strftime("%d/%m/%Y"),
            'ocupacion': paciente.ocupacion,
            'turno': turno.fecha.strftime("%d/%m/%Y %H:%M") if turno else None,
            'obras_sociales': obras_sociales
        }
        resultados.append(resultado)

    # Si no hay resultados, se muestra un mensaje de alerta, no se muestra en caso de que si haya resultados
    mensaje = "No se encontraron pacientes con esa busqueda" if not resultados else None
    return render_template('index.html', resultados_busqueda=resultados, mensaje=mensaje)

# Ruta para la navegacion de index.html a nuevo_paciente.html
@app.route('/nuevo_paciente')
def nuevo_paciente():
    return render_template('nuevo_paciente.html')

 # funcion para agregar un nuevo paciente a la base de datos
@app.route('/agregar_paciente', methods=['POST'])
def agregar_paciente():
    # Obtenemos los datos del formulario
    medico = request.form.get('medico')
    historia_clinica = request.form.get('historia_clinica')
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    dni = request.form.get('dni')
    sexo = request.form.get('sexo')
    mail = request.form.get('mail')
    telefono = request.form.get('telefono')
    telefono_celular = request.form.get('telefono_celular')
    nacionalidad = request.form.get('nacionalidad')
    domicilio = request.form.get('domicilio')
    fecha_nacimiento = datetime.strptime(request.form.get('fecha_nacimiento'), '%Y-%m-%d')
    ocupacion = request.form.get('ocupacion')
    obra_social_1 = request.form.get('obras_sociales[0][nombre]')
    num_afiliado_1 = request.form.get('obras_sociales[0][num_afiliado]')
    obra_social_2 = request.form.get('obras_sociales[1][nombre]')
    num_afiliado_2 = request.form.get('obras_sociales[1][num_afiliado]')
    
    # Creamos el nuevo paciente con los datos recibidos
    paciente = Paciente(
        medico=medico,
        historia_clinica=historia_clinica,
        nombre_paciente=nombre,
        apellido=apellido,
        dni=dni,
        sexo=sexo,
        mail=mail,
        telefono=telefono,
        telefono_celular=telefono_celular,
        nacionalidad=nacionalidad,
        domicilio=domicilio,
        fecha_nacimiento=fecha_nacimiento,
        ocupacion=ocupacion,
        obra_social_1=obra_social_1,
        num_afiliado_1=num_afiliado_1,
        obra_social_2=obra_social_2,
        num_afiliado_2=num_afiliado_2
        )
    
    db.session.add(paciente)
    db.session.commit()

    # Confirmamos que el paciente se agrego correctamente
    mensaje = "El paciente se agrego correctamente"
    return render_template('nuevo_paciente.html', mensaje=mensaje)

    # Ruta para la navegacion de index.html a turnos.html
@app.route('/turnos')
def turnos():
    return render_template('turnos.html')

    # Ruta para generar lso turnos desde el formulario de html
@app.route('/generar_turnos', methods=['POST'])
def reservar_turnos():
    try:
        # Datos del formulario
        nombre_apellido = request.form.get('nombre_apellido', '').strip()
        fecha = datetime.strptime(request.form.get('fecha'), "%Y-%m-%d").date()
        hora_inicio = datetime.strptime(request.form.get('hora_inicio'), "%H:%M").time()
        hora_fin = datetime.strptime(request.form.get('hora_fin'), "%H:%M").time()

        # Separar nombre y apellido
        partes_nombre = nombre_apellido.split()
        if len(partes_nombre) < 2:
            raise ValueError("Por favor, ingrese el nombre y el apellido del paciente.")

        nombre = " ".join(partes_nombre[:-1])  # Todas las palabras menos la última (nombre)
        apellido = partes_nombre[-1]  # La última palabra (apellido)

        # Buscar el paciente en la base de datos
        paciente = Paciente.query.filter_by(nombre_paciente=nombre, apellido=apellido).first()

        if not paciente:
            raise ValueError("No se encontró un paciente con ese nombre y apellido.")


        turnos_creados = []
        # Genera turnos mientras que la hora actual no sea mayor que la hora final
        if hora_inicio < hora_fin:
            turno = Turno(
                nombre_apellido=nombre_apellido,
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
            )
            db.session.add(turno)
            turnos_creados.append(turno)
    
        db.session.commit()
        flash("Recordatorio generado correctamente")
        return render_template('turnos.html', turnos=turnos_creados)
    
    except Exception as e:
        db.session.rollback()
        flash(f"Ocurrió un error: {e}")
        return render_template('turnos.html')

@app.route('/consultar_turnos', methods=['POST'])
def consultar_turnos():
    # Obtiene el valor del input del formulario
    busqueda = request.form.get('busqueda')  
    
    # Realiza la consulta filtrando por nombre o apellido
    turnos = Turno.query.filter(
        Turno.nombre_apellido.ilike(f'%{busqueda}%') |
        Turno.fecha.ilike(f'%{busqueda}%') |
        Turno.hora_inicio.ilike(f'%{busqueda}%') |
        Turno.hora_fin.ilike(f'%{busqueda}%') |
        Turno.estado.ilike(f'%{busqueda}%') |
        Turno.tipo_turno.ilike(f'%{busqueda}%') 
    ).all()
    
    return render_template('turnos.html', turnos=turnos)

# Cada vez que cambiamos algo, el servidor se reinicia por si solo. Ademas llamamos al init de la base de datos
if __name__ == '__main__':
    init_db()
    app.run(debug=True)