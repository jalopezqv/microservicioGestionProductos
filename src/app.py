from flask             import Flask, request, jsonify
from flask_sqlalchemy  import SQLAlchemy
from flask_marshmallow import Marshmallow

import json


with open('../secret.json') as file:
    data_bd = json.load(file)

CADENA_CONEXION_BD = 'mysql+pymysql://{}:{}@localhost/bdsistemaventa'.format(data_bd['USERBD'],data_bd['PASSBD'])
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']        = CADENA_CONEXION_BD
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Producto(db.Model):
    id       = db.Column(db.Integer     , primary_key=True)
    nombre   = db.Column(db.String(50)  , unique=True)
    precio   = db.Column(db.Float)
    cantidad = db.Column(db.Integer)
    estado   = db.Column(db.Integer     , default=1)

    def __init__(self, nombre, precio, cantidad):
        self.nombre   = nombre
        self.precio   = precio
        self.cantidad = cantidad


db.create_all()


class ProductoSchema(ma.Schema):
    class Meta:
        fields = ('id', 'nombre', 'precio', 'cantidad', 'estado')


producto_schema = ProductoSchema()
productos_schema = ProductoSchema(many=True)


@app.route('/productos/crear-producto', methods=['POST'])
def crear_poducto():
    nombre   = request.json['nombre']
    precio   = request.json['precio']
    cantidad = request.json['cantidad']

    producto_nuevo = Producto(nombre, precio, cantidad)

    db.session.add(producto_nuevo)
    db.session.commit()

    resultado = producto_schema.jsonify(producto_nuevo)
    
    return resultado


@app.route('/productos/consultar-productos', methods=['GET'])
def consultar_productos():
    query     = Producto.query.filter(Producto.estado==1)
    productos = productos_schema.dump(query)
    resultado = jsonify(productos)

    return resultado


@app.route('/productos/consultar-productos/<id>', methods=['GET'])
def consultar_producto_x_id(id):
    producto = Producto.query.get(id)
    resultado = producto_schema.jsonify(producto)
    
    return resultado


@app.route('/productos/actualizar-producto/<id>', methods=['PUT'])
def actualizar_producto(id):
    producto_actualizar = Producto.query.get(id)

    nombre   = request.json['nombre']
    precio   = request.json['precio']
    cantidad = request.json['cantidad']

    producto_actualizar.nombre   = nombre
    producto_actualizar.precio   = precio
    producto_actualizar.cantidad = cantidad

    db.session.commit()

    resultado = jsonify({'mensaje':'producto actualizado correctamente'}) 

    return resultado


@app.route('/productos/inhabilitar-producto/<id>', methods=['PUT'])
def inhabilitar_producto(id):
    producto_inhabilitar = Producto.query.get(id)
    producto_inhabilitar.estado = 0
    db.session.commit()

    resultado = jsonify({'mensaje':'producto inhabilitado correctamente'}) 

    return resultado


if __name__ == '__main__':
    PORT = 5000
    app.run(debug=True, port=PORT)