from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

#Llama a flask como app
app = Flask(__name__)
#ruta de la base de datos para que SQLAlchemy pueda conectarse
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database/consultorio.db"
#Nos permite crear consultas en SQL con SQLAlchemy
db = SQLAlchemy(app)


#La ruta / es la que se utiliza para acceder a la página principal
#app.route 
@app.route('/')
def home():
    return render_template('index.html') 

# Cada vez que cambiamos algo, el servidor se reinicia por si solo
if __name__ == '__main__':
    app.run(debug=True)
