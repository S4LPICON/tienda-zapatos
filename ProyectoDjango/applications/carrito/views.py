from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect, render
from applications.productos.models import Producto
from .models import Carrito, ItemCarrito


def obtener_carrito(request):
    carrito_id = request.session.get("carrito_id")
    if carrito_id:
        carrito = Carrito.objects.filter(id=carrito_id).first()
    else:
        carrito = Carrito.objects.create()
        request.session["carrito_id"] = carrito.id
    return carrito


def agregar_al_carrito(request):
    carrito = obtener_carrito(request)

    if request.method == "POST":
        tipo = request.POST.get("tipo")

        if tipo == "local":
            producto_id = request.POST.get("producto_id")
            producto = get_object_or_404(Producto, id=producto_id)

        elif tipo == "api":
            nombre = request.POST.get("nombre")
            precio_usd = request.POST.get("precio", "0")
            descripcion = request.POST.get("descripcion", "")
            imagen = request.POST.get("imagen", "")

            # Validar que el nombre no esté vacío
            if not nombre or nombre.strip() == "":
                nombre = "Producto externo"
            
            # Validar precio y convertir de USD a COP
            try:
                precio_usd_decimal = Decimal(precio_usd)
                # Tasa de cambio aproximada: 1 USD = 3800 COP
                TASA_CAMBIO = Decimal("3800")
                precio_cop = precio_usd_decimal * TASA_CAMBIO
            except:
                precio_cop = Decimal("0")
            
            # Validar descripción
            if not descripcion or descripcion.strip() == "":
                descripcion = "Producto externo desde API"

            # Buscar o crear el producto (precio ya en COP)
            producto, created = Producto.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "precio": precio_cop,
                    "descripcion": descripcion,
                    "imagen_url": imagen,
                },
            )

            # Actualizar si ya existía pero con datos incompletos
            if not created:
                actualizar = False
                if precio_cop > 0 and producto.precio != precio_cop:
                    producto.precio = precio_cop
                    actualizar = True
                if descripcion and producto.descripcion != descripcion:
                    producto.descripcion = descripcion
                    actualizar = True
                if imagen and not producto.imagen_url:
                    producto.imagen_url = imagen
                    actualizar = True
                if actualizar:
                    producto.save()

        else:
            return redirect("tienda")

        item, creado = ItemCarrito.objects.get_or_create(
            carrito=carrito, producto=producto
        )
        if not creado:
            item.cantidad += 1
            item.save()

        return redirect("ver_carrito")

    return redirect("tienda")


def ver_carrito(request):
    carrito = obtener_carrito(request)
    return render(request, "carrito/ver_carrito.html", {"carrito": carrito})


def eliminar_del_carrito(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id)
    item.delete()
    return redirect("ver_carrito")