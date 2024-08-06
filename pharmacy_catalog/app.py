from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)

# Inicialización de la aplicación
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Cambia esto por una clave secreta fuerte
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pharmacy.db'
app.config.update(
    SESSION_COOKIE_SECURE=True,  # Solo envía cookies sobre HTTPS
    SESSION_COOKIE_HTTPONLY=True  # No accesible vía JavaScript
)
db = SQLAlchemy(app)

# Definición de los modelos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    price = db.Column(db.Float, nullable=False)

# Rutas de la aplicación
@app.route('/')
def index():
    """
    Renderiza la página de inicio con una lista de medicamentos.
    """
    medicines = Medicine.query.all()
    return render_template('index.html', medicines=medicines)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Maneja el inicio de sesión de los usuarios.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        flash('Login failed. Check your username and/or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    Maneja el cierre de sesión de los usuarios.
    """
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Maneja el registro de nuevos usuarios.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/add_medicine', methods=['GET', 'POST'])
def add_medicine():
    """
    Permite a los usuarios agregar nuevos medicamentos.
    """
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        new_medicine = Medicine(name=name, description=description, price=price)
        db.session.add(new_medicine)
        db.session.commit()
        flash('Medicine added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_medicine.html')

# Manejo de errores
@app.errorhandler(500)
def internal_error(error):
    """
    Maneja errores internos del servidor.
    """
    app.logger.error('Server Error: %s', (error))
    return "500 error", 500

@app.errorhandler(404)
def not_found_error(error):
    """
    Maneja errores de página no encontrada.
    """
    app.logger.error('Not Found: %s', (error))
    return "404 error", 404

# Creación de las tablas y ejecución de la aplicación
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
