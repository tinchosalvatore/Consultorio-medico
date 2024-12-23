from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import relationship


#Llama a flask como app
app = Flask(__name__)
#ruta de la base de datos para que SQLAlchemy pueda conectarse
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database/consultorio.db"
#Nos permite crear consultas en SQL con SQLAlchemy
db = SQLAlchemy(app)

#Aca creamos la base de datos de los pacientes, usando clases como tablas

class Paciente(db.Model):
    __tablename__ = 'pacientes'  
    
    paciente_id = db.Column(db.Integer, primary_key=True)
    nombre_paciente = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    dni = db.Column(db.Integer, nullable=False, unique=True)
    mail = db.Column(db.String(50), nullable=True)
    telefono = db.Column(db.String(20), nullable=False)
    domicilio = db.Column(db.String(50), nullable=False)
    fecha_nacimiento = db.Column(db.DateTime, nullable=False)
    ocupacion = db.Column(db.String(50), nullable=True)
    
    # Relaciones, back_populates es para evitar inconsistencias en la base de datos, actualizando los cambios bidireccionalmente
    turnos = relationship("Turno", back_populates="paciente")
    obras_sociales = relationship("ObraSocial", secondary="paciente_obra_social", back_populates="pacientes")

class ObraSocial(db.Model):
    __tablename__ = 'obras_sociales'
    
    obra_social_id = db.Column(db.Integer, primary_key=True)
    nombre_obra_social = db.Column(db.String(50), nullable=False, unique=True)
    
    # Relaciones
    pacientes = relationship("Paciente", secondary="paciente_obra_social", back_populates="obras_sociales")

class PacienteObraSocial(db.Model):
    __tablename__ = 'paciente_obra_social'
    
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.paciente_id'), primary_key=True)
    obra_social_id = db.Column(db.Integer, db.ForeignKey('obras_sociales.obra_social_id'), primary_key=True)
    numero_obra_social = db.Column(db.Integer, nullable=True)  

class Turno(db.Model):
    __tablename__ = 'turnos'
    
    turno_id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.paciente_id'), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)  # Cambiado a DateTime para incluir hora
    
    # Relaciones
    paciente = relationship("Paciente", back_populates="turnos")



#RUTAS

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
    # Query para obtener las obras sociales a las que el paciente es afiliado
    
        obras_sociales = db.session.query(ObraSocial.nombre_obra_social,PacienteObraSocial.numero_obra_social).join
        (PacienteObraSocial,ObraSocial.obra_social_id == PacienteObraSocial.obra_social_id).filter
        (PacienteObraSocial.paciente_id == Paciente.paciente_id).all()

# obtener el turno más reciente, si es que existe
    turno = Turno.query.filter_by(paciente_id = paciente.paciente_id).order_by(Turno.fecha.desc()).first()

    #Lista con los resultados de la busqueda para mostrarlos en la página
    resultado = {
        'nombre': paciente.nombre_paciente,
        'apellido': paciente.apellido,
        'dni': paciente.dni,
        'mail': paciente.mail,
        'telefono': paciente.telefono,
        'domicilio': paciente.domicilio,
        'fecha_nacimiento': paciente.fecha_nacimiento.strftime("%d/%m/%Y"),
        'ocupacion': paciente.ocupacion,
        'turno': turno.fecha.strftime("%d/%m/%Y %H:%M") if turno else None,
        'obras_sociales': obras_sociales
    }
    resultados.append(resultado)

    # Si no hay resultados, se muestra un mensaje de alerta, no se muestra en caso de que si haya resultados
    mensaje = "No se encontraron pacientes con esa busqueda" if not resultados else None
    return render_template('index.html', resultados_busqueda=resultados, mensaje=mensaje) and redirect(url_for('home'))

# Ruta para la navegacion de index.html a nuevo_paciente.html
@app.route('/nuevo_paciente')
def nuevo_paciente():
    return render_template('nuevo_paciente.html')

 # funcion para agregar un nuevo paciente a la base de datos
@app.route('/agregar_paciente', methods=['POST'])
def agregar_paciente():
    # Obtenemos los datos del formulario
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    dni = request.form.get('dni')
    mail = request.form.get('mail')
    telefono = request.form.get('telefono')
    domicilio = request.form.get('domicilio')
    fecha_nacimiento = request.form.get('fecha_nacimiento') 
    ocupacion = request.form.get('ocupacion')
    
    # Creamos el nuevo paciente con los datos recibidos
    paciente = Paciente(
        nombre_paciente=nombre,
        apellido=apellido,
        dni=dni,
        mail=mail,
        telefono=telefono,
        domicilio=domicilio,
        fecha_nacimiento=fecha_nacimiento,
        ocupacion=ocupacion
        )
    db.session.add(paciente)
    db.session.commit()


    mensaje = "El paciente se agrego correctamente"
    return render_template('agregar_paciente.html', mensaje=mensaje)




    
# Cada vez que cambiamos algo, el servidor se reinicia por si solo
if __name__ == '__main__':
    app.run(debug=True)