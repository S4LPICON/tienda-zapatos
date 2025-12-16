#!/usr/bin/env python
"""
Script para sincronizar TODOS los tipos de zapatos desde DummyJSON API.
Incluye: zapatos de mujer, hombre y calzado deportivo.
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
    print("🔄 SINCRONIZACIÓN DE ZAPATOS - TODAS LAS CATEGORÍAS")
    print("="*60 + "\n")
    
    # Paso 1: Eliminar productos anteriores
    print("1️⃣  Eliminando productos anteriores...")
    cantidad_eliminados = ProductoAPI.objects.all().delete()[0]
    print(f"   ✓ {cantidad_eliminados} productos eliminados\n")
    
    # Paso 2: Obtener zapatos de la API (todas las categorías)
    print("2️⃣  Obteniendo zapatos de la API (mujer, hombre, deportivo)...")
    productos = DummyJSONService.obtener_productos(limit=50)
    print(f"   ✓ {len(productos)} zapatos obtenidos de la API\n")
    
    if not productos:
        print("   ❌ No se pudieron obtener productos de la API")
        return
    
    # Paso 3: Obtener tasa de cambio
    print("3️⃣  Obteniendo tasa de cambio USD → COP...")
    resultado_tasa = ExchangeRateService.obtener_tasa_cambio()
    if resultado_tasa:
        tasa = resultado_tasa.get('tasa_cop', 4000.0)
        print(f"   ✓ Tasa: 1 USD = {tasa:.2f} COP\n")
    else:
        print("   ⚠️  No se pudo obtener la tasa, usando valor por defecto\n")
        tasa = 4000.0
    
    # Paso 4: Sincronizar en base de datos
    print("4️⃣  Sincronizando en base de datos...")
    contador = 0
    categorias = set()
    
    for prod in productos:
        try:
            # Extraer datos
            api_id = prod.get('id')
            titulo = prod.get('title', 'Sin título')
            descripcion = prod.get('description', '')
            precio_usd = float(prod.get('price', 0))
            categoria = prod.get('category', 'sin-categoria')
            marca = prod.get('brand', 'Sin marca')
            stock = prod.get('stock', 0)
            rating = prod.get('rating', 0)
            thumbnail = prod.get('thumbnail', '')
            
            # Calcular precio en COP
            precio_cop = precio_usd * tasa
            
            # Crear o actualizar producto
            producto, creado = ProductoAPI.objects.update_or_create(
                api_id=api_id,
                defaults={
                    'titulo': titulo,
                    'descripcion': descripcion,
                    'precio_usd': precio_usd,
                    'precio_cop': precio_cop,
                    'categoria': categoria,
                    'marca': marca,
                    'stock': stock,
                    'rating': rating,
                    'imagen_url': thumbnail,
                    'activo': True
                }
            )
            
            if creado:
                contador += 1
                categorias.add(categoria)
                print(f"   ✓ {titulo}...")
        
        except Exception as e:
            print(f"   ✗ Error con producto {prod.get('title', 'desconocido')}: {e}")
            continue
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN")
    print("="*60)
    print(f"✅ Productos sincronizados: {contador}")
    print(f"✅ Total en base de datos: {ProductoAPI.objects.count()}")
    print(f"✅ Categorías: {', '.join(sorted(categorias))}")
    print(f"✅ Tasa de cambio: 1 USD = {tasa:.2f} COP")
    print("="*60 + "\n")
    
    # Mostrar algunos ejemplos por categoría
    print("📦 EJEMPLOS DE PRODUCTOS POR CATEGORÍA:")
    print("-"*60)
    for cat in sorted(categorias):
        productos_cat = ProductoAPI.objects.filter(categoria=cat)[:2]
        print(f"\n🏷️  {cat.upper()}:")
        for p in productos_cat:
            print(f"   • {p.titulo} - ${p.precio_usd:.2f} USD (${p.precio_cop:,.0f} COP)")
    print("\n")

if __name__ == '__main__':
    main()
