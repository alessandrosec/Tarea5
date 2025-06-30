from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from pymongo.errors import OperationFailure
import traceback
from datetime import datetime

app = Flask(__name__)

# CONFIGURACIÓN DE CONEXIONES
def get_db():
    """Conecta a la base de datos inventario con usuario que tiene permisos readWrite"""
    uri = "mongodb://usuario_rw:Password123@localhost:27017/inventario?authSource=inventario"
    client = MongoClient(uri)
    return client['inventario']

def get_gestion_db(user_type='escritura'):
    """
    Conecta a la base de datos gestionUsuarios con diferentes tipos de usuario
    user_type: 'lectura' o 'escritura'
    """
    if user_type == 'lectura':
        uri = "mongodb://lectura:1234@localhost:27017/gestionUsuarios?authSource=gestionUsuarios"
    else:  # escritura
        uri = "mongodb://escritura:5678@localhost:27017/gestionUsuarios?authSource=gestionUsuarios"
    
    client = MongoClient(uri)
    return client['gestionUsuarios']

# RUTAS PRINCIPALES
@app.route('/')
def home():
    """Página principal"""
    return render_template('index.html')

@app.route('/test-connection')
def test_connection():
    """Prueba las conexiones a las bases de datos"""
    results = {}
    
    try:
        db_inventario = get_db()
        db_inventario.admin.command('ping')
        results['inventario'] = "✅ Conexión exitosa"
    except Exception as e:
        results['inventario'] = f"❌ Error: {str(e)}"
    
    try:
        db_gestion_lectura = get_gestion_db('lectura')
        db_gestion_lectura.admin.command('ping')
        results['gestion_lectura'] = "✅ Conexión exitosa"
    except Exception as e:
        results['gestion_lectura'] = f"❌ Error: {str(e)}"
    
    try:
        db_gestion_escritura = get_gestion_db('escritura')
        db_gestion_escritura.admin.command('ping')
        results['gestion_escritura'] = "✅ Conexión exitosa"
    except Exception as e:
        results['gestion_escritura'] = f"❌ Error: {str(e)}"
    
    return jsonify(results)

# EJERCICIO 17: INSERTAR DATOS
@app.route('/agregar', methods=['POST'])
def agregar():
    """Endpoint para agregar productos a la base de datos inventario"""
    db = get_db()
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se enviaron datos"}), 400
        
        # Agregar timestamp
        data['fecha_creacion'] = datetime.now().isoformat()
        
        resultado = db.productos.insert_one(data)
        
        return jsonify({
            "mensaje": "Producto insertado exitosamente",
            "insertado_id": str(resultado.inserted_id),
            "datos": data
        }), 201
        
    except OperationFailure as e:
        return jsonify({
            "error": "Error de privilegios en MongoDB",
            "detalles": str(e)
        }), 403
    except Exception as e:
        return jsonify({
            "error": "Error interno del servidor",
            "detalles": str(e)
        }), 500

@app.route('/ejercicio17')
def ejercicio17():
    """Página del ejercicio 17"""
    return render_template('index.html', ejercicio='17')

# EJERCICIO 18: VERIFICAR ERROR DE PRIVILEGIOS
@app.route('/cambiar-permisos-usuario', methods=['POST'])
def cambiar_permisos_usuario():
    """Instrucciones para cambiar permisos del usuario"""
    instrucciones = {
        "mensaje": "Para cambiar los permisos del usuario, ejecuta este comando en MongoDB:",
        "comando_mongodb": """
// Conectarse como admin
use inventario
db.updateUser("usuario_rw", {
    roles: [{ role: "read", db: "inventario" }]
})
        """,
        "para_restaurar": """
// Para restaurar permisos de escritura:
use inventario
db.updateUser("usuario_rw", {
    roles: [{ role: "readWrite", db: "inventario" }]
})
        """
    }
    return jsonify(instrucciones)

@app.route('/ejercicio18')
def ejercicio18():
    """Página del ejercicio 18"""
    return render_template('index.html', ejercicio='18')

# EJERCICIO 19: CONSULTAR PRODUCTOS
@app.route('/listar', methods=['GET'])
def listar():
    """Endpoint para listar todos los productos"""
    try:
        db = get_db()
        productos = list(db.productos.find({}, {"_id": 0}))
        
        return jsonify({
            "productos": productos,
            "total": len(productos),
            "mensaje": "Productos obtenidos exitosamente"
        }), 200
        
    except OperationFailure as e:
        return jsonify({
            "error": "Error de privilegios en MongoDB",
            "detalles": str(e)
        }), 403
    except Exception as e:
        return jsonify({
            "error": "Error interno del servidor",
            "detalles": str(e)
        }), 500

@app.route('/ejercicio19')
def ejercicio19():
    """Página del ejercicio 19"""
    return render_template('index.html', ejercicio='19')

# GESTIÓN DE USUARIOS
@app.route('/gestion-usuarios', methods=['GET', 'POST'])
def gestion_usuarios():
    """Gestión completa de usuarios"""
    mensaje = ""
    tipo_mensaje = ""
    usuarios = []
    
    try:
        db = get_gestion_db('escritura')
        
        if request.method == 'POST':
            if request.is_json:
                data = request.get_json()
                nombre = data.get('nombre')
            else:
                nombre = request.form.get('nombre')
            
            if nombre:
                try:
                    usuario_data = {
                        "nombre": nombre,
                        "fecha_creacion": datetime.now().isoformat()
                    }
                    resultado = db.usuarios.insert_one(usuario_data)
                    
                    if request.is_json:
                        return jsonify({
                            "success": True,
                            "mensaje": "Usuario insertado exitosamente",
                            "id": str(resultado.inserted_id)
                        })
                    else:
                        mensaje = "Usuario insertado exitosamente"
                        tipo_mensaje = "success"
                except Exception as e:
                    if request.is_json:
                        return jsonify({
                            "success": False,
                            "error": f"Error: {e}"
                        }), 500
                    else:
                        mensaje = f"Error: {e}"
                        tipo_mensaje = "error"
        
        usuarios = list(db.usuarios.find({}, {"_id": 0}))
        
        if request.is_json:
            return jsonify({
                "usuarios": usuarios,
                "total": len(usuarios)
            })
            
    except Exception as e:
        mensaje = f"Error de conexión: {e}"
        tipo_mensaje = "error"
        if request.is_json:
            return jsonify({"success": False, "error": mensaje}), 500

    return render_template('index.html', 
                         ejercicio='gestion', 
                         usuarios=usuarios, 
                         mensaje=mensaje, 
                         tipo_mensaje=tipo_mensaje)

@app.route('/validar-roles/<username>')
def validar_roles(username):
    """Validación de roles desde Python"""
    try:
        db = get_gestion_db('escritura')
        usuario_info = db.command("usersInfo", username)
        
        return jsonify({
            "usuario": username,
            "informacion": usuario_info,
            "mensaje": "Información de usuario obtenida exitosamente"
        })
    except Exception as e:
        return jsonify({
            "error": "Error al obtener información del usuario",
            "detalles": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True)