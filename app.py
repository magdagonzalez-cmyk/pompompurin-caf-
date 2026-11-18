import unicodedata
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'pompompurin_cafe_secreto_pastel_2026'

# Catálogo de productos (más de 4 elementos con múltiples atributos)
menu_items = [
    {
        "id": 1,
        "nombre": "Pudín Pompompurin",
        "categoria": "Postres Clásicos",
        "descripcion": "Suave pudín artesanal de vainilla y caramelo con la icónica boina de chocolate de Pompompurin.",
        "precio": 5.00,
        "imagen": "images/pudin.png"
    },
    {
        "id": 2,
        "nombre": "Roll Cake de Pompompurin",
        "categoria": "Pastelería",
        "descripcion": "Esponjoso bizcocho enrollado relleno de crema pastelera de vainilla y caramelo dulce.",
        "precio": 6.50,
        "imagen": "images/roll_cake.png"
    },
    {
        "id": 3,
        "nombre": "Panqueques Pompompurin",
        "categoria": "Desayunos y Meriendas",
        "descripcion": "Torre de tres panqueques dorados bañados en miel de maple con decoración de Pompompurin.",
        "precio": 7.00,
        "imagen": "images/panqueques.png"
    },
    {
        "id": 4,
        "nombre": "Galletas Pompompurin",
        "categoria": "Galletas y Bocaditos",
        "descripcion": "Crujientes galletas de mantequilla horneadas diariamente con glaseado suave de cacao.",
        "precio": 4.00,
        "imagen": "images/galletas.png"
    },
    {
        "id": 5,
        "nombre": "Donut Pompompurin",
        "categoria": "Pastelería",
        "descripcion": "Dona esponjosa glaseada con crema de plátano dulce, orejitas de chocolate y boina de cacao.",
        "precio": 4.50,
        "imagen": "images/donut.png"
    },
    {
        "id": 6,
        "nombre": "Profiteroles Pompompurin",
        "categoria": "Postres Clásicos",
        "descripcion": "Delicados bocaditos rellenos de crema chantilly de vainilla con cobertura de chocolate.",
        "precio": 6.00,
        "imagen": "images/profiteroles.png"
    }
]

galeria_items = [
    {
        "titulo": "Rincón del Pudín",
        "categoria": "Ambiente",
        "descripcion": "Nuestra mesa principal decorada en tonos crema y caramelo para disfrutar en compañía."
    },
    {
        "titulo": "Taza Especial de la Casa",
        "categoria": "Merchandising",
        "descripcion": "Taza coleccionable con huellita de Pompompurin incluida en combos seleccionados."
    },
    {
        "titulo": "Repostería Temática Diaria",
        "categoria": "Cocina",
        "descripcion": "Cada postre es decorado a mano por nuestros pasteleros cada mañana."
    },
    {
        "titulo": "Amigos del Café",
        "categoria": "Personajes",
        "descripcion": "Muffin, Scone y Bagel acompañan cada rincón de nuestra cafetería virtual."
    }
]

usuarios_db = {
    "purin@cafe.com": {
        "nombre": "Pompompurin Fan",
        "email": "purin@cafe.com",
        "password": generate_password_hash("123456"),
        "pedidos": [
            {
                "numero": "PED-1001",
                "fecha": "15/11/2026 16:30",
                "estado": "Entregado",
                "total": 11.50,
                "items": ["Pudín Pompompurin", "Roll Cake de Pompompurin"]
            }
        ]
    }
}

def normalizar_texto(texto):
    """Elimina tildes y convierte a minúsculas para búsquedas flexibles."""
    texto_nfd = unicodedata.normalize('NFD', texto.lower().strip())
    return ''.join(c for c in texto_nfd if unicodedata.category(c) != 'Mn')

def filtrar_productos(lista, consulta="", categoria="Todas"):
    resultado = lista
    if categoria and categoria != "Todas":
        resultado = [p for p in resultado if p["categoria"] == categoria]
    if consulta:
        q_norm = normalizar_texto(consulta)
        resultado = [
            p for p in resultado
            if q_norm in normalizar_texto(p["nombre"])
            or q_norm in normalizar_texto(p["descripcion"])
            or q_norm in normalizar_texto(p["categoria"])
        ]
    return resultado

def obtener_carrito():
    carrito_ids = session.get('carrito', [])
    items_carrito = []
    total = 0.0
    for idx, item_id in enumerate(carrito_ids):
        producto = next((p for p in menu_items if p["id"] == item_id), None)
        if producto:
            items_carrito.append({
                "index": idx,
                "id": producto["id"],
                "nombre": producto["nombre"],
                "precio": producto["precio"],
                "imagen": producto["imagen"]
            })
            total += producto["precio"]
    return items_carrito, total

def usuario_actual():
    email = session.get('usuario_email')
    if email and email in usuarios_db:
        return usuarios_db[email]
    return None

@app.context_processor
def inyectar_datos_globales():
    items_carrito, _ = obtener_carrito()
    return dict(
        usuario=usuario_actual(),
        carrito_count=len(items_carrito),
        busqueda_global=request.args.get('q', '')
    )

@app.route('/')
def inicio():
    consulta = request.args.get('q', '').strip()
    productos_filtrados = filtrar_productos(menu_items, consulta=consulta)
    items_carrito, total = obtener_carrito()
    return render_template(
        'index.html',
        productos=productos_filtrados,
        consulta=consulta,
        carrito=items_carrito,
        total=total,
        pagina_activa='inicio'
    )

@app.route('/menu')
def menu():
    categoria_filtro = request.args.get('categoria', 'Todas')
    consulta = request.args.get('q', '').strip()
    filtrados = filtrar_productos(menu_items, consulta=consulta, categoria=categoria_filtro)
    categorias = ['Todas'] + sorted(list(set(p["categoria"] for p in menu_items)))
    items_carrito, total = obtener_carrito()
    return render_template(
        'menu.html',
        productos=filtrados,
        categorias=categorias,
        categoria_actual=categoria_filtro,
        consulta=consulta,
        carrito=items_carrito,
        total=total,
        pagina_activa='menu'
    )

@app.route('/sobre')
def sobre():
    return render_template(
        'sobre.html',
        galeria=galeria_items,
        pagina_activa='sobre'
    )

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    enviado = False
    nombre_usuario = ""
    if request.method == 'POST':
        nombre_usuario = request.form.get('nombre', '')
        enviado = True
    return render_template(
        'contacto.html',
        enviado=enviado,
        nombre_usuario=nombre_usuario,
        pagina_activa='contacto'
    )

# --- RUTAS DE AUTENTICACIÓN, CUENTA Y PEDIDOS ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if usuario_actual():
        return redirect(url_for('cuenta'))

    aviso_compra = request.args.get('motivo') == 'compra'

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = usuarios_db.get(email)

        if user and check_password_hash(user['password'], password):
            session['usuario_email'] = email
            flash(f"¡Bienvenido de nuevo, {user['nombre']}!", "success")
            siguiente = session.pop('despues_login', None)
            if siguiente == 'comprar':
                return redirect(url_for('finalizar_compra_automatica'))
            return redirect(url_for('cuenta'))
        else:
            flash("Correo o contraseña incorrectos. Inténtalo nuevamente o regístrate.", "error")

    return render_template(
        'login.html',
        aviso_compra=aviso_compra,
        pagina_activa='cuenta'
    )

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if usuario_actual():
        return redirect(url_for('cuenta'))

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirmar = request.form.get('confirmar_password', '')

        if not nombre or not email or not password:
            flash("Por favor completa todos los campos.", "error")
        elif email in usuarios_db:
            flash("Ya existe una cuenta registrada con ese correo electrónico.", "error")
        elif password != confirmar:
            flash("Las contraseñas no coinciden.", "error")
        else:
            usuarios_db[email] = {
                "nombre": nombre,
                "email": email,
                "password": generate_password_hash(password),
                "pedidos": []
            }
            session['usuario_email'] = email
            flash(f"¡Cuenta creada con éxito! Bienvenido/a a Pompompurin Café, {nombre}.", "success")
            siguiente = session.pop('despues_login', None)
            if siguiente == 'comprar':
                return redirect(url_for('finalizar_compra_automatica'))
            return redirect(url_for('cuenta'))

    return render_template('registro.html', pagina_activa='cuenta')

@app.route('/cuenta')
def cuenta():
    user = usuario_actual()
    if not user:
        flash("Inicia sesión o regístrate para ver tu perfil y tus pedidos.", "info")
        return redirect(url_for('login'))

    items_carrito, total_carrito = obtener_carrito()
    return render_template(
        'cuenta.html',
        user=user,
        pedidos=list(reversed(user['pedidos'])),
        carrito=items_carrito,
        total_carrito=total_carrito,
        pagina_activa='cuenta'
    )

@app.route('/logout')
def logout():
    session.pop('usuario_email', None)
    flash("Has cerrado sesión correctamente. ¡Vuelve pronto!", "info")
    return redirect(url_for('inicio'))

# --- CARRITO Y FINALIZACIÓN DE COMPRA ---

@app.route('/agregar/<int:producto_id>', methods=['POST'])
def agregar_carrito(producto_id):
    carrito = session.get('carrito', [])
    carrito.append(producto_id)
    session['carrito'] = carrito
    return redirect(request.referrer or url_for('inicio'))

@app.route('/eliminar_item/<int:index>', methods=['POST'])
def eliminar_item(index):
    carrito = session.get('carrito', [])
    if 0 <= index < len(carrito):
        carrito.pop(index)
        session['carrito'] = carrito
    return redirect(request.referrer or url_for('inicio'))

def registrar_pedido_usuario(user, items_carrito, total):
    numero_pedido = f"PED-{1001 + len(user['pedidos'])}"
    nuevo_pedido = {
        "numero": numero_pedido,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "estado": "En preparación",
        "total": total,
        "items": [item["nombre"] for item in items_carrito]
    }
    user['pedidos'].append(nuevo_pedido)
    session['carrito'] = []
    return numero_pedido

@app.route('/comprar', methods=['POST'])
def comprar():
    items_carrito, total = obtener_carrito()
    if not items_carrito:
        flash("Tu carrito está vacío. Agrega tus postres favoritos primero.", "info")
        return redirect(url_for('inicio'))

    user = usuario_actual()
    if not user:
        session['despues_login'] = 'comprar'
        flash("Para finalizar tu compra y guardar tu pedido, inicia sesión o crea una cuenta.", "info")
        return redirect(url_for('login', motivo='compra'))

    numero = registrar_pedido_usuario(user, items_carrito, total)
    flash(f"¡Pedido {numero} confirmado por ${total:.2f}! Ya puedes verlo en tu historial.", "success")
    return redirect(url_for('cuenta'))

@app.route('/finalizar_compra_automatica')
def finalizar_compra_automatica():
    user = usuario_actual()
    items_carrito, total = obtener_carrito()
    if user and items_carrito:
        numero = registrar_pedido_usuario(user, items_carrito, total)
        flash(f"¡Gracias por registrarte/iniciar sesión! Tu pedido {numero} por ${total:.2f} ha sido confirmado.", "success")
    return redirect(url_for('cuenta'))

if __name__ == '__main__':
    app.run(debug=True)
