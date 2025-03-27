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
    dni = db.Column(db.Text, nullable=True)
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
@app.route('/subir_csv', methods=['GET', 'POST'])
def subir_archivo():
    if request.method == 'POST':
        archivo = request.files['archivo_csv']
        if archivo:
            try:
                contenido = archivo.read().decode('utf-8')
                import io
                # Detectar el delimitador - prueba con '|' si el CSV usa barras verticales
                # o usa ',' como predeterminado
                delimiter = ',' 
                csv_reader = csv.DictReader(io.StringIO(contenido), delimiter=delimiter)
                
                # Imprime las cabeceras para depuración
                print("Cabeceras del CSV:", csv_reader.fieldnames)
                
                for fila in csv_reader:
                    # Mapea correctamente los nombres de las columnas - ajusta según las cabeceras reales
                    paciente = Paciente(
                        nombre_paciente=fila.get('Nombre', ''),  # Nota la 'N' mayúscula
                        apellido=fila.get('Apellido', ''),       # Nota la 'A' mayúscula
                        dni=fila.get('DNI', ''),                 # Usa el nombre correcto de la columna
                        # ... mapea el resto de los campos correctamente
                        medico=fila.get('Cuadro combinado44', ''),
                        historia_clinica=fila.get('Número HC', ''),
                        sexo=fila.get('Sexo', ''),
                        mail=fila.get('E-mail', ''),
                        telefono=fila.get('TE', ''),
                        telefono_celular=fila.get('TEL Movil', ''),
                        nacionalidad=fila.get('Nacionalidad', ''),
                        domicilio=fila.get('Dirección', ''),
                        fecha_nacimiento=fila.get('Fecha de Nacimiento', ''),
                        ocupacion=fila.get('Ocupación', ''),
                        obra_social_1=fila.get('Cuadro combinado40', ''),
                        num_afiliado_1=fila.get('N_Afil', ''),
                        # Para la segunda obra social, puedes utilizar otros campos del CSV
                        # o dejarlos vacíos si no corresponden
                        obra_social_2='',
                        num_afiliado_2=''
                    )
                    
                    # Evitar insertar registros si el DNI está vacío o ya existe
                    if paciente.dni:
                        existing = Paciente.query.filter_by(dni=paciente.dni).first()
                        if not existing:
                            db.session.add(paciente)
                
                db.session.commit()
                return "Pacientes cargados exitosamente."
            except Exception as e:
                db.session.rollback()
                return f"Ocurrió un error: {e}"
      
    return render_template('subir_csv.html')

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
            'fecha_nacimiento': paciente.fecha_nacimiento,
            'ocupacion': paciente.ocupacion,
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
    
    # Obtener obras sociales correctamente
    obras_sociales = request.form.getlist('obras_sociales[][nombre]')
    num_afiliados = request.form.getlist('obras_sociales[][num_afiliado]')

    # Validar si hay al menos una obra social
    obra_social_1 = obras_sociales[0] if len(obras_sociales) > 0 and obras_sociales[0] else None
    num_afiliado_1 = num_afiliados[0] if len(num_afiliados) > 0 and num_afiliados[0] else None
    obra_social_2 = obras_sociales[1] if len(obras_sociales) > 1 and obras_sociales[1] else None
    num_afiliado_2 = num_afiliados[1] if len(num_afiliados) > 1 and num_afiliados[1] else None
    
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

@app.route('/ultimo_paciente')
def ultimo_paciente():
    # Obtener el último paciente añadido
    ultimo = Paciente.query.order_by(Paciente.paciente_id.desc()).first()
    
    if not ultimo:
        return render_template('ultimo_paciente.html', paciente=None, mensaje="No hay pacientes registrados.")
    
    # Preparar los datos del último paciente de manera similar a la búsqueda
    obras_sociales = []
    if ultimo.obra_social_1:
        obras_sociales.append({'nombre': ultimo.obra_social_1, 'num_afiliado': ultimo.num_afiliado_1})
    if ultimo.obra_social_2:
        obras_sociales.append({'nombre': ultimo.obra_social_2, 'num_afiliado': ultimo.num_afiliado_2})

    paciente = {
        'id': ultimo.paciente_id,
        'medico': ultimo.medico,
        'historia_clinica': ultimo.historia_clinica,
        'nombre': ultimo.nombre_paciente,
        'apellido': ultimo.apellido,
        'dni': ultimo.dni,
        'sexo': ultimo.sexo,
        'mail': ultimo.mail,
        'telefono': ultimo.telefono,
        'telefono_celular': ultimo.telefono_celular,
        'nacionalidad': ultimo.nacionalidad,
        'domicilio': ultimo.domicilio,
        'fecha_nacimiento': ultimo.fecha_nacimiento,
        'ocupacion': ultimo.ocupacion,
        'obras_sociales': obras_sociales
    }
    
    return render_template('ultimo_paciente.html', paciente=paciente)

@app.route('/editar_paciente', methods=['GET'])
def mostrar_editar_paciente():
    # Render the search page for editing patients
    return render_template('editar_paciente.html', resultados_busqueda=[], mensaje=None)

@app.route('/buscar_paciente_editar', methods=['POST'])
def buscar_paciente_editar():
    busqueda = request.form.get('busqueda')

    # Query to find patients matching the search
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
        obras_sociales = []
        if paciente.obra_social_1:
            obras_sociales.append({'nombre': paciente.obra_social_1, 'num_afiliado': paciente.num_afiliado_1})
        if paciente.obra_social_2:
            obras_sociales.append({'nombre': paciente.obra_social_2, 'num_afiliado': paciente.num_afiliado_2})

        resultado = {
            'id': paciente.paciente_id,  # Important: Include ID for editing
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
            'fecha_nacimiento': paciente.fecha_nacimiento,
            'ocupacion': paciente.ocupacion,
            'obras_sociales': obras_sociales
        }
        resultados.append(resultado)

    # If no results, show an alert message
    mensaje = "No se encontraron pacientes con esa búsqueda" if not resultados else None
    return render_template('editar_paciente.html', resultados_busqueda=resultados, mensaje=mensaje)


@app.route('/editar_paciente/<int:paciente_id>', methods=['GET'])
def formulario_editar_paciente(paciente_id):
    # Find the patient by ID
    paciente = Paciente.query.get_or_404(paciente_id)
    
    # Prepare obras sociales data
    obras_sociales = []
    if paciente.obra_social_1:
        obras_sociales.append({
            'nombre': paciente.obra_social_1, 
            'num_afiliado': paciente.num_afiliado_1
        })
    if paciente.obra_social_2:
        obras_sociales.append({
            'nombre': paciente.obra_social_2, 
            'num_afiliado': paciente.num_afiliado_2
        })
    
    return render_template('formulario_editar_paciente.html', paciente={
        'id': paciente.paciente_id,
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
        'fecha_nacimiento': paciente.fecha_nacimiento,
        'ocupacion': paciente.ocupacion,
        'obras_sociales': obras_sociales
    })

@app.route('/actualizar_paciente/<int:paciente_id>', methods=['POST'])
def actualizar_paciente(paciente_id):
    try:
        # Find the patient by ID
        paciente = Paciente.query.get_or_404(paciente_id)
        
        # Update patient fields from form
        paciente.medico = request.form.get('medico')
        paciente.historia_clinica = request.form.get('historia_clinica')
        paciente.nombre_paciente = request.form.get('nombre')
        paciente.apellido = request.form.get('apellido')
        paciente.dni = request.form.get('dni')
        paciente.sexo = request.form.get('sexo')
        paciente.mail = request.form.get('mail')
        paciente.telefono = request.form.get('telefono')
        paciente.telefono_celular = request.form.get('telefono_celular')
        paciente.nacionalidad = request.form.get('nacionalidad')
        paciente.domicilio = request.form.get('domicilio')
        paciente.fecha_nacimiento = request.form.get('fecha_nacimiento')
        paciente.ocupacion = request.form.get('ocupacion')
        
        # Handle obras sociales
        paciente.obra_social_1 = request.form.get('obras_sociales[0][nombre]', '')
        paciente.num_afiliado_1 = request.form.get('obras_sociales[0][num_afiliado]', '')
        paciente.obra_social_2 = request.form.get('obras_sociales[1][nombre]', '')
        paciente.num_afiliado_2 = request.form.get('obras_sociales[1][num_afiliado]', '')
        
        # Commit changes
        db.session.commit()
        
        # Success message
        mensaje = f"Paciente {paciente.nombre_paciente} {paciente.apellido} actualizado correctamente"
        return render_template('editar_paciente.html', mensaje=mensaje, resultados_busqueda=[])
    
    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        mensaje = f"Ocurrió un error al actualizar el paciente: {str(e)}"
        return render_template('editar_paciente.html', mensaje=mensaje, resultados_busqueda=[])
    

@app.route('/eliminar_paciente', methods=['GET'])
def mostrar_eliminar_paciente():
    # Simplemente renderizamos la plantilla para eliminar pacientes
    return render_template('eliminar_paciente.html', resultados_busqueda=[], mensaje=None)

@app.route('/buscar_paciente_eliminar', methods=['POST'])
def buscar_paciente_eliminar():
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
        obras_sociales = []
        if paciente.obra_social_1:
            obras_sociales.append({'nombre': paciente.obra_social_1, 'num_afiliado': paciente.num_afiliado_1})
        if paciente.obra_social_2:
            obras_sociales.append({'nombre': paciente.obra_social_2, 'num_afiliado': paciente.num_afiliado_2})

        resultado = {
            'id': paciente.paciente_id,  # Importante: Incluir el ID para poder eliminar
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
            'fecha_nacimiento': paciente.fecha_nacimiento,
            'ocupacion': paciente.ocupacion,
            'obras_sociales': obras_sociales
        }
        resultados.append(resultado)

    # Si no hay resultados, se muestra un mensaje de alerta
    mensaje = "No se encontraron pacientes con esa búsqueda" if not resultados else None
    return render_template('eliminar_paciente.html', resultados_busqueda=resultados, mensaje=mensaje)

@app.route('/confirmar_eliminar/<int:paciente_id>', methods=['POST'])
def confirmar_eliminar(paciente_id):
    try:
        # Buscamos el paciente por ID
        paciente = Paciente.query.get_or_404(paciente_id)
        
        # Guardamos nombre y apellido para mensaje de confirmación
        nombre_completo = f"{paciente.nombre_paciente} {paciente.apellido}"
        
        # Eliminamos el paciente
        db.session.delete(paciente)
        db.session.commit()
        
        # Mensaje de éxito
        mensaje = f"El paciente {nombre_completo} ha sido eliminado correctamente"
        return render_template('eliminar_paciente.html', resultados_busqueda=[], mensaje=mensaje, tipo_mensaje="success")
    
    except Exception as e:
        # En caso de error, hacemos rollback
        db.session.rollback()
        mensaje = f"Ocurrió un error al eliminar el paciente: {str(e)}"
        return render_template('eliminar_paciente.html', resultados_busqueda=[], mensaje=mensaje, tipo_mensaje="error")


# Cada vez que cambiamos algo, el servidor se reinicia por si solo. Ademas llamamos al init de la base de datos
if __name__ == '__main__':
    init_db()
    app.run(debug=True)