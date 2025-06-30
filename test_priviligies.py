# test_privileges.py
from pymongo import MongoClient
from pymongo.errors import OperationFailure

def test_privilege_error():
    """Función para probar errores de privilegios"""
    
    # Modificar usuario para solo lectura
    admin_client = MongoClient("mongodb://admin:adminPassword123@localhost:27017/?authSource=admin")
    db_admin = admin_client['inventario']
    
    try:
        # Cambiar permisos del usuario
        db_admin.command("updateUser", "usuario_rw", 
                        roles=[{"role": "read", "db": "inventario"}])
        print("✓ Usuario modificado a solo lectura")
        
        # Probar inserción (debería fallar)
        client_rw = MongoClient("mongodb://usuario_rw:Password123@localhost:27017/inventario?authSource=inventario")
        db = client_rw['inventario']
        
        try:
            resultado = db.productos.insert_one({"nombre": "Producto Test", "precio": 100})
            print("✗ ERROR: La inserción debería haber fallado")
        except OperationFailure as e:
            print(f"✓ Error esperado de privilegios: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_privilege_error()