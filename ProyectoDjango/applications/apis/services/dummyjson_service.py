"""
Servicio para consumir API de DummyJSON (productos).
API 1: Obtiene datos de productos de prueba.
"""
import requests
from datetime import datetime
from ..db.mongodb import mongo_db

API_URL = "https://dummyjson.com/products"

# Categorías relacionadas con calzado/zapatos
CATEGORIAS_ZAPATOS = ['shoes', 'mens-shoes', 'womens-shoes', 'sports-shoes', 'footwear']

class DummyJSONService:
    """Servicio para interactuar con la API de DummyJSON"""
    
    @staticmethod
    def obtener_productos(limit=30):
        """
        Consume la API externa DummyJSON para obtener productos de zapatos.
        SOLO zapatos reales: hombre y mujer.
        Excluye equipos deportivos.
        Almacena el historial de consultas en MongoDB.
        """
        try:
            productos = []
            
            # SOLO categorías de zapatos reales (sin accesorios deportivos)
            categorias_zapatos = [
                'womens-shoes',  # Zapatos de mujer
                'mens-shoes',    # Zapatos de hombre
            ]
            
            # Obtener productos de cada categoría
            for categoria in categorias_zapatos:
                try:
                    response = requests.get(f"{API_URL}/category/{categoria}", timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        productos_categoria = data.get('products', [])
                        
                        # Filtrar para asegurar que son zapatos
                        for prod in productos_categoria:
                            titulo = prod.get('title', '').lower()
                            # Excluir productos que claramente no son zapatos
                            palabras_excluir = ['ball', 'bat', 'helmet', 'glove', 'wicket', 
                                              'shuttlecock', 'racket', 'rim', 'football', 
                                              'basketball', 'baseball', 'volleyball', 'tennis ball',
                                              'cricket', 'golf ball', 'iron golf']
                            
                            if not any(palabra in titulo for palabra in palabras_excluir):
                                productos.append(prod)
                except:
                    continue
            
            # Si no se obtuvieron productos de categorías, buscar por palabra clave
            if not productos:
                response = requests.get(f"{API_URL}/search?q=shoes", timeout=10)
                response.raise_for_status()
                data = response.json()
                productos = data.get('products', [])
            
            # Limitar resultados
            productos = productos[:limit]
            
            # Guardar en MongoDB el historial de consulta
            DummyJSONService._guardar_historial({
                "tipo": "obtener_productos_zapatos",
                "fecha": datetime.now(),
                "cantidad": len(productos),
                "categorias": categorias_zapatos,
                "exitoso": True,
                "datos": productos[:3]  # Guardar solo los primeros 3 como muestra
            })
            
            return productos
        except requests.RequestException as e:
            DummyJSONService._guardar_historial({
                "tipo": "obtener_productos_zapatos",
                "fecha": datetime.now(),
                "cantidad": 0,
                "exitoso": False,
                "error": str(e)
            })
            return []
    
    @staticmethod
    def obtener_producto_por_id(producto_id):
        """Obtiene un producto específico por ID"""
        try:
            response = requests.get(f"{API_URL}/{producto_id}", timeout=10)
            response.raise_for_status()
            producto = response.json()
            
            DummyJSONService._guardar_historial({
                "tipo": "obtener_producto_por_id",
                "producto_id": producto_id,
                "fecha": datetime.now(),
                "exitoso": True,
                "datos": producto
            })
            
            return producto
        except requests.RequestException as e:
            DummyJSONService._guardar_historial({
                "tipo": "obtener_producto_por_id",
                "producto_id": producto_id,
                "fecha": datetime.now(),
                "exitoso": False,
                "error": str(e)
            })
            return None
    
    @staticmethod
    def buscar_productos(query):
        """Busca productos por nombre (enfocado en zapatos)"""
        try:
            # Si la búsqueda no incluye "shoe", agregar contexto de calzado
            search_query = query
            if 'shoe' not in query.lower() and 'zapato' not in query.lower():
                search_query = f"{query} shoes"
            
            response = requests.get(f"{API_URL}/search?q={search_query}", timeout=10)
            response.raise_for_status()
            data = response.json()
            productos = data.get("products", [])
            
            DummyJSONService._guardar_historial({
                "tipo": "buscar_productos",
                "query": search_query,
                "fecha": datetime.now(),
                "cantidad": len(productos),
                "exitoso": True
            })
            
            return productos
        except requests.RequestException as e:
            DummyJSONService._guardar_historial({
                "tipo": "buscar_productos",
                "query": query,
                "fecha": datetime.now(),
                "exitoso": False,
                "error": str(e)
            })
            return []
    
    @staticmethod
    def _guardar_historial(datos):
        """Guarda el historial de consultas en MongoDB"""
        try:
            collection = mongo_db.get_collection('historial_dummyjson')
            collection.insert_one(datos)
        except Exception as e:
            print(f"Error al guardar en MongoDB: {e}")
    
    @staticmethod
    def obtener_historial(limit=50):
        """Obtiene el historial de consultas desde MongoDB"""
        try:
            collection = mongo_db.get_collection('historial_dummyjson')
            historial = list(collection.find().sort("fecha", -1).limit(limit))
            return historial
        except Exception as e:
            print(f"Error al obtener historial: {e}")
            return []
