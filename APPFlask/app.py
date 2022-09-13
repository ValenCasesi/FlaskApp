import os
from flask import Flask
from flask import render_template, request, redirect, session
import pymysql
from datetime import datetime
from flask import send_from_directory

app=Flask(__name__)
app.secret_key="develoteca"


def obtener_conexion():
    return pymysql.connect(host='localhost',user='pela',password='asd',db='pythonlib')

@app.route('/')
def inicio():
    return render_template('sitio/index.html')

@app.route('/img/<imagen>')
def imagenes(imagen):
    return send_from_directory(os.path.join('templates/sitio/images'),imagen)

@app.route("/css/<archivocss>")
def css_link(archivocss):
    return send_from_directory(os.path.join('templates/sitio/css'),archivocss)

@app.route('/libros')
def libros():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM LIBROS")
    libros=cursor.fetchall()
    conexion.commit()
    return render_template('sitio/libros.html',libros=libros)

@app.route('/nosotros')
def nosotros():
    return render_template('sitio/nosotros.html')

@app.route('/admin/')
def admin_index():
    if not 'login' in session:
       return redirect("/admin/login") 
    return render_template('admin/index.html')

@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')

@app.route('/admin/login',methods=['POST'])
def admin_login_post():
    _usuario= request.form['txtUsuario']
    _password= request.form['txtPassword']
    
    if _usuario=="admin" and _password=="123":
        session["login"]=True
        session["usuario"]="Administrador"
        return redirect("/admin")

    return render_template("admin/login.html", mensaje="Acceso denegado - Usuario y/o contraseña incorrectos")

@app.route('/admin/cerrar')
def admin_login_cerrar():
    session.clear()
    return redirect("/admin/login")

@app.route('/admin/libros')
def admin_libros():

    if not 'login' in session:
       return redirect("/admin/login") 

    conexion=obtener_conexion()
    cursor= conexion.cursor()
    cursor.execute("SELECT * FROM LIBROS")
    libros=cursor.fetchall()
    conexion.commit()
    return render_template('admin/libros.html',libros=libros)

@app.route('/admin/libros/guardar', methods=['POST'])
def admin_libros_guardar():

    if not 'login' in session:
       return redirect("/admin/login") 

    _nombre=request.form['txtNombre']
    _url=request.form['txtURL']
    _archivo=request.files['txtImagen']
    tiempo = datetime.now()
    horaActual= tiempo.strftime('%Y%H%M%S')

    if _archivo.filename != "":
        nuevoNombre = horaActual+"_"+_archivo.filename
        _archivo.save("templates/sitio/images/"+nuevoNombre)


    sql = "INSERT INTO `pythonlib`.`libros` (`nombre`, `imagen`, `url`) VALUES (%s, %s, %s);"
    datos=(_nombre,nuevoNombre,_url)
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(sql,datos)
    conexion.commit()
    return redirect('/admin/libros')

@app.route('/admin/libros/borrar', methods=['POST'])
def admin_borrar():

    if not 'login' in session:
       return redirect("/admin/login") 

    _id=request.form['txtID']

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT imagen FROM LIBROS WHERE idlibros=%s",(_id))
    libro=cursor.fetchall()
    conexion.commit()

    if os.path.exists("templates/sitio/images/"+str(libro[0][0])):
        os.unlink("templates/sitio/images/"+ str(libro[0][0]))

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM LIBROS WHERE idlibros=%s",(_id))
    conexion.commit()

    return redirect('/admin/libros')

if __name__ == '__main__':
    app.run(debug=True)