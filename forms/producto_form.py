# Archivo: forms/producto_form.py

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ProductoForm(FlaskForm):
    """Formulario para validar la creación y edición de productos"""
    nombre = StringField('Nombre del Producto', validators=[DataRequired(message="El nombre es obligatorio")])
    cantidad = IntegerField('Cantidad en Stock', validators=[
        DataRequired(message="Ingresa una cantidad válida"), 
        NumberRange(min=0, message="La cantidad no puede ser negativa")
    ])
    precio = FloatField('Precio Unitario ($)', validators=[
        DataRequired(message="Ingresa un precio válido"), 
        NumberRange(min=0.01, message="El precio debe ser mayor a 0")
    ])
    submit = SubmitField('Guardar Producto')