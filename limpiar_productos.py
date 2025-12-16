#!/usr/bin/env python
"""
Script para limpiar productos mal creados en la base de datos local.
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ProyectoDjango'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProyectoDjango.settings.local')
django.setup()

from applications.productos.models import Producto

def main():
    print("\n" + "="*60)
    print("🧹 LIMPIEZA DE PRODUCTOS LOCALES")
    print("="*60 + "\n")
    
    # Buscar productos problemáticos
    productos_vacios = Producto.objects.filter(precio=0)
    productos_sin_descripcion = Producto.objects.filter(descripcion__in=["Producto externo (API)", ""])
    productos_sin_imagen = Producto.objects.filter(imagen__isnull=True, imagen_url__isnull=True)
    
    print(f"📊 Productos con precio $0: {productos_vacios.count()}")
    print(f"📊 Productos sin descripción real: {productos_sin_descripcion.count()}")
    print(f"📊 Productos sin imagen: {productos_sin_imagen.count()}\n")
    
    # Mostrar productos problemáticos
    productos_problema = Producto.objects.filter(
        precio=0
    ) | Producto.objects.filter(
        descripcion__in=["Producto externo (API)", ""]
    )
    
    if productos_problema.exists():
        print("⚠️  PRODUCTOS PROBLEMÁTICOS:")
        print("-"*60)
        for p in productos_problema:
            print(f"ID {p.id}: {p.nombre} - ${p.precio} - {p.descripcion[:30]}")
        print("-"*60 + "\n")
        
        respuesta = input("¿Deseas eliminar estos productos? (s/n): ")
        if respuesta.lower() == 's':
            cantidad = productos_problema.delete()[0]
            print(f"\n✅ {cantidad} productos eliminados")
        else:
            print("\n❌ No se eliminaron productos")
    else:
        print("✅ No hay productos problemáticos\n")
    
    # Mostrar productos actuales
    print("\n📦 PRODUCTOS ACTUALES EN BASE DE DATOS LOCAL:")
    print("-"*60)
    for p in Producto.objects.all():
        print(f"\n✓ {p.nombre}")
        print(f"  Precio: ${p.precio}")
        print(f"  Descripción: {p.descripcion[:50]}...")
        print(f"  Imagen: {'✅' if p.imagen or p.imagen_url else '❌'}")
    print("-"*60 + "\n")

if __name__ == '__main__':
    main()
