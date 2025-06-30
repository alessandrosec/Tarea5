# db_connection.py
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

def get_db(database_name="inventario"):
    """
    Establece conexión con MongoDB usando autenticación
    """
    try:
        uri = f"mongodb://usuario_rw:Password123@localhost:27017/{database_name}?authSource={database_name}"
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # Verificar conexión
        client.admin.command('ping')
        return client[database_name]
    except ConnectionFailure:
        print("Error: No se pudo conectar a MongoDB")
        return None
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

def test_connection():
    """Función para probar la conexión"""
    db = get_db()
    if db:
        print("✓ Conexión exitosa a MongoDB")
        return True
    else:
        print("✗ Error de conexión")
        return False

if __name__ == "__main__":
    test_connection()