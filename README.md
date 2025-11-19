# PracticoIntegradorFinal
# Sistema de Inventario – Django + Docker

Sistema de inventario desarrollado con **Django 5.2.8** y **PostgreSQL 15**, como práctica para la Tecnicatura en Desarrollo de Software.

Permite gestionar:

- Productos y stock
- Clientes
- Ventas con ítems de venta
- Roles de usuario por grupo (*administradores*, *stock*, *ventas*)

Los datos iniciales (usuarios, grupos, productos, clientes y algunas ventas de ejemplo) se cargan automáticamente desde `backup.json` al levantar el proyecto con Docker.

usuario root → contraseña: Practica1Final
usuario stocker → contraseña: inventario25
usuario vendedor → contraseña: ventas25

## 🚀 Funcionalidades

### Autenticación y roles

- Autenticación con **django-allauth** (solo *login* y *logout*; el registro está deshabilitado).
- Vista de inicio (*home*) que se muestra solo a usuarios autenticados.
- Uso de **LoginRequiredMixin** y **PermissionRequiredMixin** en las vistas para restringir acceso según permisos/grupos.
- Tres grupos principales:
  - **administradores**: acceso completo al sistema (productos, stock, clientes y ventas).
  - **stock**: acceso de lectura/escritura a productos y movimientos de stock.
  - **ventas**: acceso de lectura/escritura a clientes y ventas.


### Módulo Productos

- Modelo **Producto** con campos como:
  - nombre, descripción, precio, SKU, stock actual, stock mínimo, etc.
- ABM completo:
  - `producto_list.html`: listado con tabla y paginación.
  - `producto_form.html`: alta/edición usando **django-crispy-forms** + **bootstrap4**.
  - `producto_delete.html`: pantalla de confirmación antes de eliminar.
  - `producto_detail.html`: detalle de un producto, con últimos movimientos de stock y acceso a ajuste.
- Gestión de stock:
  - Modelo **MovimientoStock**: registra entradas y salidas de stock (producto, tipo, cantidad, motivo, fecha, usuario).
  - `MovimientoStockCreateView`: formulario para crear movimientos de stock manuales.
  - **Ajuste de stock**:
    - Vista `AjusteStockView`: permite fijar una nueva cantidad absoluta de stock para un producto.
    - Calcula la diferencia respecto del stock actual y genera automáticamente un `MovimientoStock` (entrada o salida).
    - No permite cantidades negativas.
  - Vista `MovimientoStockListView`: listado de movimientos asociados a un producto.
- Vista de **stock bajo**:
  - `StockBajoListView`: muestra productos cuyo stock actual está por debajo del stock mínimo.

Todas las vistas relacionadas con productos/stock están protegidas para que solo accedan usuarios de los grupos **stock** o **administradores** (o superusuario).

---

### Módulo Clientes

- Modelo **Cliente** con campos:
  - nombre, apellido, número de documento (único), email, teléfono, dirección, etc.
- ABM completo:
  - `cliente_list.html`: búsqueda y paginación (por nombre, apellido o documento).
  - `cliente_form.html`: alta/edición con crispy-forms.
  - `cliente_detail.html`: ficha de cliente.
  - `cliente_delete.html`: confirmación de borrado.
- Protección al borrar:
  - Si un cliente tiene ventas asociadas, la vista de borrado captura la excepción **ProtectedError** y:
    - no elimina el cliente,
    - muestra un mensaje explicando que no se puede eliminar porque tiene ventas registradas,
    - redirige de vuelta al detalle del cliente.

Las vistas de clientes están restringidas a usuarios de grupos **ventas** o **administradores** (o superusuario).

---

### Módulo Ventas

- Modelo **Venta**:
  - código de venta, cliente, fecha, total.
- Modelo **ItemVenta**:
  - venta, producto, cantidad, precio unitario, subtotal.
- Alta de venta:
  - Vista de creación (`VentaCreateView`) que combina:
    - un `VentaForm` para la cabecera, y
    - un `ItemVentaFormSet` para las líneas de ítems.
  - Se utiliza **django-crispy-forms** para maquetar el formulario y el formset.
  - Al guardar:
    - se calcula el subtotal de cada ítem,
    - se calcula el total de la venta,
    - se descuenta el stock de cada producto involucrado.
- Listado y detalle:
  - `venta_list.html`: listado de ventas con búsqueda por código/cliente.
  - `venta_detail.html`: muestra cabecera (cliente, fecha, total) y todos los ítems (producto, cantidad, precio, subtotal).

Las vistas de ventas están restringidas a usuarios de grupos **ventas** o **administradores** (o superusuario).

---

## 🛠️ Tecnologías

- **Backend**
  - Python 3.11
  - Django 5.2.8
  - django-allauth
  - django-crispy-forms + crispy-bootstrap4
- **Base de datos**
  - PostgreSQL 15 (corriendo en contenedor Docker)
- **Frontend**
  - Bootstrap 4
- **Infraestructura**
  - Docker
  - Docker Compose

---

## 📁 Estructura del proyecto

En la carpeta raíz del proyecto (`inventario/`):

```text
inventario/
├── accounts/          # App para implementar logueo
├── clientes/          # App de clientes (modelos, vistas, forms, urls)
├── core/              # Componentes compartidos (helpers, mixins, etc.)
├── inventario/        # Configuración del proyecto (settings, urls, wsgi)
├── media/             # Archivos subidos (si aplica)
├── productos/         # App de productos, stock y movimientos
├── static/            # Archivos estáticos (CSS, JS, imágenes)
├── templates/         # Templates base y compartidos (home, login, etc.)
├── ventas/            # App de ventas e ítems de venta
├── .dockerignore
├── .env               # Variables de entorno (NO subir credenciales reales)
├── .gitignore
├── backup.json        # Datos de ejemplo (dump de la BD para loaddata)
├── docker-compose.yml # Definición de servicios (web, db)
├── Dockerfile         # Imagen de la app Django
├── manage.py
└── requirements.txt   # Dependencias de Python
