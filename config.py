import os
from pymongo import MongoClient

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuraciones de MongoDB
    MONGO_HOST = os.environ.get('MONGO_HOST') or 'localhost'
    MONGO_PORT = int(os.environ.get('MONGO_PORT') or 27017)
    
    # URIs de conexión para diferentes usuarios
    MONGO_URIS = {
        'inventario_rw': f"mongodb://usuario_rw:Password123@{MONGO_HOST}:{MONGO_PORT}/inventario?authSource=inventario",
        'gestion_lectura': f"mongodb://lectura:1234@{MONGO_HOST}:{MONGO_PORT}/gestionUsuarios?authSource=gestionUsuarios",
        'gestion_escritura': f"mongodb://escritura:5678@{MONGO_HOST}:{MONGO_PORT}/gestionUsuarios?authSource=gestionUsuarios",
        'ventas_admin': f"mongodb://admin_ventas:admin123@{MONGO_HOST}:{MONGO_PORT}/ventas?authSource=ventas"
    }

def get_database_connection(db_key):
    """
    Obtiene una conexión a la base de datos específica
    """
    try:
        uri = Config.MONGO_URIS.get(db_key)
        if not uri:
            raise ValueError(f"No se encontró configuración para {db_key}")
        
        client = MongoClient(uri)
        # Extraer nombre de la base de datos del URI
        db_name = uri.split('/')[-1].split('?')[0]
        return client[db_name]
    except Exception as e:
        print(f"Error conectando a la base de datos {db_key}: {e}")
        raise