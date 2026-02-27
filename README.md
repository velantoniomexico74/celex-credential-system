RECUPERACIÓN CELEX – PROCEDIMIENTO COMPLETO
1. Instalar dependencias del sistema
sudo apt update
sudo apt install python3 python3-venv python3-pip
________________________________________
2. Clonar repositorio
git clone <URL_REPO>
cd celex
________________________________________
3. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate
4. Instalar dependencias
pip install -r requirements.txt
5. Crear estructura necesaria
mkdir uploads fotos credenciales
6. Ejecutar sistema
venv/bin/python app.py
7. Acceder
http://148.204.180.44:5000
4. Instalar dependencias
pip install -r requirements.txt
________________________________________
5. Crear estructura necesaria
mkdir uploads fotos credenciales
________________________________________
6. Ejecutar sistema
venv/bin/python app.py
________________________________________
7. Acceder
http://148.204.180.44:5000
