
#________________________________IMPORTACIONES_________________________________

from flask import Flask
from flask import render_template, request, redirect, url_for, flash
from flaskext.mysql import MySQL
from flask import send_from_directory
from datetime import datetime
import os 

#________________________________DEFINIR VARIABLES_________________________________

app = Flask(__name__)
app.secret_key="Develoteca"

CARPETA = os.path.join('uploads')
app.config['CARPETA'] = CARPETA

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)

#________________________________CONFIGURAR DB_________________________________

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = "localhost" 
app.config['MYSQL_DATABASE_USER'] = "root" 
app.config['MYSQL_DATABASE_PASSWORD'] = "" 
app.config['MYSQL_DATABASE_DB'] = "sistema"

mysql.init_app(app) 

#________________________________INDEX_________________________________

@app.route('/')
def index():

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empleados")

    empleados = cursor.fetchall()
    #print(empleados)
    conn.commit()

    return render_template('empleados/index.html', empleados = empleados)

#________________________________BORRAR DATO_________________________________

@app.route('/destroy/<int:id>')
def destroy(id):

    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT foto FROM empleados WHERE id = %s", id)
    fila=cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))

    cursor.execute('DELETE FROM empleados WHERE id = %s', (id))

    conn.commit()

    return redirect('/')

#________________________________EDITAR DATOS_________________________________

@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM empleados WHERE id = %s', (id))

    empleados = cursor.fetchall()
    conn.commit()

    return render_template('empleados/edit.html', empleados = empleados)


@app.route('/update', methods = ['POST'])
def update():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    _id = request.form['txtID']

    if _nombre == "" or _correo == "" or _foto == "":
        flash('No puedes dejar campos vacios puto')
        return redirect(url_for('edit', id = _id))

    sql = "UPDATE empleados SET nombre=%s, correo=%s WHERE id = %s;"
    datos = (_nombre, _correo, _id)
    conn = mysql.connect()
    cursor = conn.cursor()

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename != "":
        nuevoNombreFoto = tiempo +"_"+ _foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

        cursor.execute("SELECT foto FROM empleados WHERE id = %s", _id)
        fila=cursor.fetchall()

        os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
        cursor.execute("UPDATE empleados SET foto = %s WHERE id = %s", (nuevoNombreFoto, _id))
        
        conn.commit()

    cursor.execute(sql, datos)

    conn.commit()

    return redirect("/")

#________________________________INSERTAR DATOS_________________________________

@app.route('/create')
def create():
    return render_template("empleados/create.html")


#________________________________GUARDAR DATOS_________________________________

@app.route('/store', methods = ['POST'])
def storage():

    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']

    if _nombre == "" or _correo == "" or _foto == "":
        flash('Recuerda llenar los datos de los campos')
        return redirect(url_for('create'))

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename != "":
        nuevoNombreFoto = tiempo +"_"+ _foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

    sql = "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s, %s);"
    datos = (_nombre, _correo, nuevoNombreFoto)
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute(sql, datos)

    conn.commit()

    return redirect('/')


#________________________________DEBUG_________________________________

if __name__ == '__main__':
    app.run(debug = True)
