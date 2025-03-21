# 📌 Consultorio-medico 🏥
Este repositorio va a ser usado por la **secretaria** de un consultorio.  
La secretaria podrá llevar cómodamente un seguimiento de los datos de los pacientes, con la posibilidad de **agregar** y **eliminar** registros.  

Además, tiene una funcionalidad para **importar** archivos CSV con datos de la base de datos anterior.  
Por otro lado, los **médicos** también tendrán acceso a toda la información necesaria sobre los pacientes.  


## ⚡ Instalación y ejecución local 💻
### 📋 Requisitos previos  
Antes de comenzar, asegúrate de tener instalado:  
- **Python 3.x**  
- **pip** (gestor de paquetes de Python)  
- **Git** 
### 📂 Clonar el repositorio con SSH
```bash
git clone git@github.com:tinchosalvatore/Consultorio-medico.git
cd consultorio-medico
```

Hay dos scripts, el primero siendo ``install.sh`` para instalar todas las dependencias y el segundo ``boot.sh`` para ejecutar la app en local
Hay que darle permisos de ejecución a ambos
```
chmod +x install.sh
chmod +x boot.sh
```
Para ejecutarlos
```
./install.sh
./boot.sh
```
## Tecnologías usadas
### ⚙️ Backend ⚙️
- **Python**
- **Flask**
- **SQLite**
### 🎨 Frontend 🎨
- **html**
- **CSS**

Las dependencias están bien listadas en el `requirements.txt`, incluyendo sus versiones

# 📌 Autor y mantenimiento 🛠️✨

Esta aplicación fue desarrollada completamente por @tinchosalvatore, incluyendo tanto el backend como el frontend.
El proyecto puede recibir futuras actualizaciones con nuevas funcionalidades y correcion de bugs.

Si tienes sugerencias o encuentras algún problema, ¡no dudes en abrir un issue o contactarme! 🚀