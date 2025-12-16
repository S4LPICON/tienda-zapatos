#!/usr/bin/env python
"""
Script de prueba para verificar que el carrito funciona correctamente
con productos de la API.
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ProyectoDjango'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProyectoDjango.settings.local')
django.setup()

from applications.productos.models import Producto
from applications.carrito.models import Carrito, ItemCarrito
from decimal import Decimal

def main():
    print("\n" + "="*60)
    print("🧪 TEST: Verificar productos en 'Nuestros Productos'")
    print("="*60 + "\n")
    
    # Verificar productos locales
    productos = Producto.objects.all()
    
    print(f"📦 Total de productos en Producto (locales): {productos.count()}\n")
    
    if productos.exists():
        print("📋 LISTA DE PRODUCTOS:")
        print("-"*60)
        for p in productos:
            print(f"\nID: {p.id}")
            print(f"Nombre: {p.nombre}")
            print(f"Precio: ${p.precio}")
            print(f"Descripción: {p.descripcion[:50]}..." if p.descripcion else "Sin descripción")
            print(f"Imagen: {p.imagen if p.imagen else 'No tiene imagen física'}")
            print(f"Imagen URL: {p.imagen_url if p.imagen_url else 'No tiene URL'}")
            print(f"Imagen a mostrar: {p.imagen_mostrar}")
            print("-"*60)
    else:
        print("⚠️  No hay productos en la base de datos local")
    
    print("\n" + "="*60)
    print("🧪 TEST: Simular agregar producto de API al carrito")
    print("="*60 + "\n")
    
    # Simular agregar producto de API
    nombre_test = "Nike Air Jordan 1 Test"
    precio_test = Decimal("99.99")
    descripcion_test = "Zapatos deportivos de alta calidad"
    imagen_test = "https://cdn.dummyjson.com/products/images/mens-shoes/Nike-Air-Jordan-1-Red-And-Black/1.png"
    
    print(f"Creando producto de prueba:")
    print(f"  Nombre: {nombre_test}")
    print(f"  Precio: ${precio_test}")
    print(f"  Descripción: {descripcion_test}")
    print(f"  Imagen: {imagen_test}\n")
    
    producto, created = Producto.objects.get_or_create(
        nombre=nombre_test,
        defaults={
            "precio": precio_test,
            "descripcion": descripcion_test,
            "imagen_url": imagen_test,
        },
    )
    
    if created:
        print("✅ Producto creado exitosamente")
    else:
        print("ℹ️  Producto ya existía, verificando datos...")
        actualizar = False
        if producto.precio != precio_test:
            producto.precio = precio_test
            actualizar = True
        if producto.descripcion != descripcion_test:
            producto.descripcion = descripcion_test
            actualizar = True
        if not producto.imagen_url and imagen_test:
            producto.imagen_url = imagen_test
            actualizar = True
        if actualizar:
            producto.save()
            print("✅ Producto actualizado")
    
    # Verificar datos del producto
    print("\n📋 DATOS DEL PRODUCTO GUARDADO:")
    print("-"*60)
    print(f"ID: {producto.id}")
    print(f"Nombre: {producto.nombre}")
    print(f"Precio: ${producto.precio}")
    print(f"Descripción: {producto.descripcion}")
    print(f"Imagen URL: {producto.imagen_url}")
    print(f"Imagen a mostrar: {producto.imagen_mostrar}")
    print("-"*60)
    
    # Crear carrito y agregar producto
    print("\n🛒 Agregando al carrito...")
    carrito = Carrito.objects.create()
    item, creado = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        producto=producto
    )
    
    if creado:
        print("✅ Producto agregado al carrito exitosamente")
    else:
        print("ℹ️  Producto ya estaba en el carrito")
    
    print(f"\n📊 Subtotal del item: ${item.subtotal()}")
    print(f"📊 Total del carrito: ${carrito.total()}")
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETADO")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
