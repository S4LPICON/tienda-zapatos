#!/usr/bin/env python
"""
Script para limpiar productos antiguos y sincronizar solo zapatos/calzado
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ProyectoDjango'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProyectoDjango.settings.local')
django.setup()

from applications.apis.models import ProductoAPI
from applications.apis.services.dummyjson_service import DummyJSONService
from applications.apis.services.exchangerate_service import ExchangeRateService

def main():
    print("\n" + "="*60)
    print("🧹 LIMPIEZA Y SINCRONIZACIÓN DE ZAPATOS")
    print("="*60)
    
    # Eliminar productos antiguos
    print("\n1️⃣ Eliminando productos anteriores...")
    count = ProductoAPI.objects.all().count()
    ProductoAPI.objects.all().delete()
    print(f"   ✓ {count} productos eliminados")
    
    # Obtener productos de zapatos
    print("\n2️⃣ Obteniendo zapatos de la API...")
    productos = DummyJSONService.obtener_productos(limit=30)
    print(f"   ✓ {len(productos)} zapatos obtenidos de la API")
    
    # Obtener tasa de cambio
    print("\n3️⃣ Obteniendo tasa de cambio...")
    tasas = ExchangeRateService.obtener_tasa_cambio()
    tasa_cop = tasas['tasa_cop'] if tasas else 4000
    print(f"   ✓ Tasa: 1 USD = {tasa_cop:.2f} COP")
    
    # Sincronizar en base de datos
    print("\n4️⃣ Sincronizando en base de datos...")
    sincronizados = 0
    
    for prod_data in productos:
        precio_cop = float(prod_data.get('price', 0)) * tasa_cop
        
        producto, created = ProductoAPI.objects.update_or_create(
            api_id=prod_data.get('id'),
            defaults={
                'titulo': prod_data.get('title', ''),
                'descripcion': prod_data.get('description', ''),
                'precio_usd': prod_data.get('price', 0),
                'precio_cop': precio_cop,
                'categoria': prod_data.get('category', ''),
                'marca': prod_data.get('brand', ''),
                'stock': prod_data.get('stock', 0),
                'rating': prod_data.get('rating', 0),
                'imagen_url': prod_data.get('thumbnail', ''),
                'activo': True,
            }
        )
        
        if created:
            sincronizados += 1
            print(f"   ✓ {producto.titulo[:50]}...")
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN")
    print("="*60)
    print(f"✅ Productos sincronizados: {sincronizados}")
    print(f"✅ Total en base de datos: {ProductoAPI.objects.count()}")
    print(f"✅ Categorías: {', '.join(ProductoAPI.objects.values_list('categoria', flat=True).distinct())}")
    print("\n" + "="*60)
    print("🎉 ¡Sincronización completada!")
    print("="*60)
    print("\n📍 Accede a: http://127.0.0.1:8000/apis/productos/")

if __name__ == '__main__':
    main()
