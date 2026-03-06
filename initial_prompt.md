Aplicación FIWARE mejorada

**Práctica 2 - Gestión de Datos en Entornos Inteligentes**

# Objetivo

Aplicación de gestión de una cadena de supermercados usando FIWARE.

# Flujo de trabajo para implementación

Implementar las funcionalidades y características de la aplicación usando el flujo de trabajo GitHub Flow:

- En VS Code, con el agente Plan de GitHub Copilot, elaborar un plan de implementación del _issue_ (fix/feature) a resolver.
- Crear un _issue_ en el repo remoto GitHub con el contenido del plan de implementación obtenido.
- Crear una rama git para llevar a cabo la implementación.
- Confirmar cambios (_commit_) en local y subir (_push_) la nueva rama al repo remoto.
- Finalizar con una fusión (_merge_) de la nueva rama a la rama _main_ y sincronizarla con _origin/main_. Si no somos los propietarios del repo remoto, crearemos una PR (_Pull Request_) con la nueva rama. El propietario del repo remoto deberá revisar la PR y fusionarla con _main_.

Actualizar _PRD.md_, _architecture.md_ y _data_model.md_ siempre después de finalizar la implementación de un _issue_. Es conveniente indicar esto en _AGENTS.md_.

# Tecnologías
Python Flask con plantillas Jinja2.

# Modelo de datos
Sigue el estándar NGSIv2 de FIWARE. Hay ejemplos de algunas de las entidades (aunque no incluyen todos los atributos) en el script import-data.

- Tipo entidad **Store**. Atributos: 
    - id 
    - name
    - address
    - location
    - url
    - telephone
    - countryCode (2 caracteres)
    - capacity (metros cúbicos
    - description (texto amplio)
    - temperature
    - relativeHumidity
    - tweets
- Tipo de entidad **Product**. Atributos: 
    - id
    - name
    - price (euros)
    - size ('XS', 'S', 'M', 'L', 'XL')
    - color (color RGB en hexadecimal)
- Tipo de entidad **Shelf**. Atributos: 
    - id
    - name
    - location
    - maxCapacity
    - refStore 
- Tipo de entidad **InventoryItem**. Atributos: 
    - id 
    - refProduct
    - refStore
    - refShelf
    - stockCount
    - shelfCount
- Tipo de entidad **Employee**. Atributos: 
    - id
    - name
    - image
    - salary
    - role ('Manager', etc.), 
    - refStore
    - email
    - dateOfContract
    - skills ('MachineryDriving', 'WritingReports', 'CustomerRelationships')
    - username
    - password

- Crear el **diagrama de entidades UML** usando Mermaid y mostrarlo renderizado en el apartado _About_ de la aplicación.

# Formularios de entrada de datos

- Utilizar el mayor número de elementos HTML input distintos.
- Incluir las reglas de validación HTML y JS apropiadas.

# Proveedores de contexto externo

La aplicación correrá contra el despliegue de contenedores Docker del tutorial FIWARE NGSIv2 "Context Providers". Para levantar los contenedores, se debe ejecutar "./services start" y para tirarlos "./services stop". Nunca usar docker-compose.yml directamente sino a través del script services.

Los atributos temperature y relativeHumidity de un Store serán proporcionados por un proveedor de contexto externo (la aplicación que corre en el contenedor "tutorial"). El atributo tweets de un Store también será proporcionado por un proveedor externo (de nuevo, la aplicación que corre en el contenedor "tutorial"). El registro de estos dos proveedores externos en Orion debe hacerse al arrancar la aplicación.

# Suscripciones a Orion

En nuestra aplicación recibiremos desde Orion las notificaciones **cambio de precio de un Producto** y **bajo stock de un Producto en una Tienda**. Para ello, usaremos el mecanismo de suscripciones NGSIv2 de Orion. 

El alta de estas suscripciones en Orion se efectúa mediante POST /v2/subscriptions con los siguientes JSON como cuerpo.

- Suscripción "Product price change":
{
  "description": "Product price change",
  "subject": {
    "entities": [
      {
        "idPattern": ".*", "type": "Product"
      }
    ],
     "condition": {
      "attrs": [ "price" ]
    }
  },
  "notification": {
    "http": {
      "url": "http://host.docker.internal:5000/subscription/price-change"
    }
  }
}

- Suscripción "Low stock in Store 001":
{
  "description": "Low stock in Store 001",
  "subject": {
    "entities": [
      {
        "idPattern": ".*",
        "type": "InventoryItem"
      }
    ],
     "condition": {
      "attrs": [
        "shelfCount"
      ],
      "expression": {
        "q": "shelfCount<10;refStore==urn:ngsi-ld:Store:001"
      }
    }
  },
  "notification": {
    "http": {
      "url": "http://host.docker.internal:5000/subscription/low-stock-store001"
    },
    "attrsFormat" : "keyValues"
  }
}

- Suscripciones "Low stock" para los Stores 002, 003 y 004, de modo análogo.

- Enviar notificaciones desde el servidor al navegador para que se actualicen los elementos de la interfaz de usuario involucrados. Usar Flask-SocketIO en el servidor y Socket.IO en el navegador.

# Interfaz de usuario HTML + CSS + JS pura

Como principios generales:

- Cuando algo se pueda hacer tanto mediante CSS como mediante JS, usar CSS.
- Evitar al máximo generar código HTML en el código JS. Siempre que se pueda, el código JS deberá actualizar el valor de los atributos elementos HTML ya presentes en la página en lugar de añadir nuevos elementos.

Para implementar los aspectos visuales que se piden, consultar la **sección** [**HowTo de W<sup>3</sup> Schools**](https://www.w3schools.com/howto/default.asp), que contiene multitud de **"recetas"** a este respecto.

## Estructura de la interfaz

- Vistas **_Products_, _Stores_ y _Employees_**
  - Mostrar la lista de entidades como una **tabla** donde **cada entidad incluirá su imagen, su nombre y dos enlaces tipo botón de borrado y modificación**. Además, cada entidad en la tabla mostrará los siguientes **atributos específicos**:

- _Product_: _color_, _size_
- _Store_: _countryCode_, _temperature_, _relativeHumidity_
- _Employee_: _category_, _skills_
  - Añadir al principio de la vista un enlace tipo **botón para añadir una nueva entidad**.

- Vista **_Product_**
  - Mostrar la **tabla de _InventoryItems_ agrupada por _Store_**: para cada _Store_, mostrar una fila con el nombre del _Store_ y el valor de _stockCount_ para ese producto y, a continuación, las filas de con los valores de _shelfCount_ para las distintas _Shelfs_ que contienen ese _Product_.
  - En cada encabezado de grupo _Store_ añadir un botón tipo enlace que permita **añadir un _InventoryItem_ con ese _Product_ a otra _Shelf_** que no sea ninguna de las que ya contiene ese _Product_. Los posibles valores de la _Shelf_ para el nuevo _InventoryItem_ deben restringirse mediante un elemento tipo _select_ que cargue dinámicamente las _Shelfs_ de ese _Store_ que todavía no contengan ese _Product_.
- Vista **_Store_**
  - Mostrar la **tabla de _InventoryItems_ agrupada por _Shelf_**: para cada _Shelf_, mostrar una fila con su id y su nivel de llenado (utilizar una barra de progreso) y, a continuación, las filas de con los _Products_, incluyendo sus atributos _name_, _price_, _size_, _color_, _stockCount_ y _shelfCount_.
  - Añadir un botón tipo enlace que permita **añadir una _Shelf_ a ese _Store_**.
  - En cada encabezado de grupo _Shelf_ añadir un botón tipo enlace que permita **modificar los datos de esa _Shelf_**.
  - En cada encabezado de grupo _Shelf_ añadir un botón tipo enlace que permita **añadir un _InventoryItem_ de otro _Product_** que todavía no esté presente en esa _Shelf_. Los posibles valores de _Product_ para el nuevo _InventoryItem_ deben restringirse mediante un elemento tipo _select_ que cargue dinámicamente los _Products_ existentes que todavía no estén presentes en esa _Shelf_.
  - Incluir en cada _InventoryItem_ un botón tipo enlace que permita **comprar una unidad de ese producto**. Para ello, utiliza la siguiente petición a Orion:

PATCH _/v2/entities/&lt;inventoryitem_id&gt;/attrs_

Body:

{

"shelfCount": {"type":"Integer", "value": {"\$inc": -1}},

"stockCount": {"type":"Integer", "value": {"\$inc": -1}}

}

- 1. Incluir la información de la **temperatura y humedad** relativa utilizando iconos y colores diferentes en función de los valores que tomen. Mostrar el valor numérico al lado del cada icono.
  - Incluir los **_tweets_ de ese Store** después de la tabla de _InventoryItems_. Usar un icono que recuerde a X (Twitter) a la izquierda de cada _tweet_.
  - Incluir un **apartado de notificaciones**, donde se mostrará cada notificación que se reciba (p. ej. la notificación de _stock_ bajo para alguno de los productos del _Store_).

- Cuando se reciba una **notificación de cambio de precio** de un producto, **reflejar dicho cambio en todas las vistas** donde aparece.

## Aspectos visuales

- En la vista **_Employee_**, incluir la **foto del empleado** con una transición CSS que **amplie la foto** cuando se pasa el ratón por encima de ella.
- En la vista **_Store_**, incluir una **foto del almacén** con una transición CSS que **amplíe la foto** y, al mismo tiempo, una animación CSS que **rote la imagen 360 grados**.
- Para la barra de progreso que indica el nivel de llenado de una **_Shelf_**, utilizar distintos **colores según el nivel de llenado**.
- Utilizar **colores, iconos, elementos visuales, etc. para compactar la información mostrada**, especialmente en las vistas con **tablas**. Utilizar, p. ej. los iconos de Font Awesome, escogiendo de modo adecuado. P. ej. los siguientes atributos se pueden mostrar de esta forma:

- _color_: con un cuadrado del color correspondiente.
- _country_: con un icono con la bandera del país.
- _category_: con un icono distinto según la categoría.
- _skills_: con iconos que muestren los distintos valores.

- La **barra de navegación** deberá resaltar la sección (_Home / Products / Stores / Employees_) activa en cada momento y permanecer visible cuando se efectúe _scroll_.
- Añadir una **pestaña _Stores Map_** a la barra de navegación. Esta vista mostrará las imágenes de los _Stores_ sobre el mapa. Cuando se pase el ratón sobre un Store, se deberá mostrar una tarjeta (imagen + texto) con sus atributos principales. Cuando se pulse sobre un _Store_, se deberá acceder a su página de detalle.
