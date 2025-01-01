import csv
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import relationship


#Llama a flask como app
app = Flask(__name__)
#ruta de la base de datos para que SQLAlchemy pueda conectarse
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///consultorio.db"
#Nos permite crear consultas en SQL con SQLAlchemy
db = SQLAlchemy(app)

#Aca creamos la base de datos de los pacientes, usando clases como tablas
class Paciente(db.Model):
    __tablename__ = 'pacientes'  
    
    paciente_id = db.Column(db.Integer, primary_key=True)
    medico = db.Column(db.String(50), nullable=True)
    historia_clinica = db.Column(db.Integer, nullable=True)
    nombre_paciente = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    dni = db.Column(db.Integer, nullable=True, unique=True)
    sexo = db.Column(db.String(50), nullable=True)
    mail = db.Column(db.String(50), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    telefono_celular = db.Column(db.String(20), nullable=True)
    nacionalidad = db.Column(db.String(50), nullable=True)
    domicilio = db.Column(db.String(50), nullable=True)
    fecha_nacimiento = db.Column(db.DateTime, nullable=True)
    ocupacion = db.Column(db.String(50), nullable=True)
    obra_social_1 = db.Column(db.String(50), nullable=True)
    num_afiliado_1 = db.Column(db.Integer, nullable=True)
    obra_social_2 = db.Column(db.String(50), nullable=True)
    num_afiliado_2 = db.Column(db.Integer, nullable=True)
    
    # Relaciones, back_populates es para evitar inconsistencias en la base de datos, actualizando los cambios bidireccionalmente
    turnos = relationship("Turno", back_populates="paciente")

class Turno(db.Model):
    __tablename__ = 'turnos'
    
    turno_id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.paciente_id'), nullable=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False) 
    estado = db.Column(db.String(20), nullable=True)
    
    # Relaciones
    paciente = relationship("Paciente", back_populates="turnos")

    # Esta funcion inicializa la base de datos
def init_db():
    with app.app_context():
        # db.create_all()
        db.drop_all() 

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
        turno = Turno.query.filter_by(paciente_id = paciente.paciente_id).order_by(Turno.fecha.desc()).first()
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
def mostrar_turnos():
    # Obtenemos los turnos libres y ocupados y los pasamos a la plantilla de turnos.html como variables
    turnos_libres = Turno.query.filter_by(ocupado=False).all()
    turnos_ocupados = Turno.query.filter_by(ocupado=True).all()
    return render_template('turnos.html', turnos_libres=turnos_libres, turnos_ocupados=turnos_ocupados)

    # Ruta para asignar un turno a un paciente
@app.route('/asignar_turno/<int:turno_id>', methods=['POST'])
def asignar_turno(turno_id):
    # Obtenemos los datos del formulario
    paciente_id = request.form.get('paciente_id')

    turno = Turno.query.get(turno_id)
    if turno and turno.ocupado == False:
        turno.paciente_id = paciente_id
        turno.ocupado = True
        db.session.commit()
        mensaje = "Turno asignado correctamente"
        return render_template('turnos.html', mensaje=mensaje)
    else:
        mensaje_fail = "Turno no disponible"
        return render_template('turnos.html', mensaje=mensaje_fail)
    

# Cada vez que cambiamos algo, el servidor se reinicia por si solo. Ademas llamamos al init de la base de datos
if __name__ == '__main__':
    init_db()
    app.run(debug=True)