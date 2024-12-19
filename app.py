from flask import Flask, render_template
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
    numero_obra_social = db.Column(db.Integer(50), nullable=True)  

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
    return render_template('index.html') 

#ruta para el input de busqueda de datos del paciente
@app.route('/buscar_paciente', methods=['POST'])
def buscar_paciente():
    return # Despues ver el ejemplo del chatgpt


# Cada vez que cambiamos algo, el servidor se reinicia por si solo
if __name__ == '__main__':
    app.run(debug=True)
