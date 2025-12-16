import requests

API_URL = "https://dummyjson.com/products"

def obtener_productos_api():
    """
    Obtiene productos de zapatos desde DummyJSON.
    SOLO zapatos reales: womens-shoes y mens-shoes.
    Excluye equipos deportivos como pelotas, bates, etc.
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
                response = requests.get(f"{API_URL}/category/{categoria}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    productos_categoria = data.get("products", [])
                    
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
        
        # Si no se obtuvieron productos, buscar específicamente "shoes"
        if not productos:
            response = requests.get(f"{API_URL}/search?q=shoes", timeout=5)
            response.raise_for_status()
            data = response.json()
            productos = data.get("products", [])
        
        return productos[:20]  # Limitar a 20 productos
    
    except requests.RequestException as e:
        print(f"Error obteniendo productos desde DummyJSON: {e}")
        return []
