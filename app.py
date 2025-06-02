from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from sqlalchemy import create_engine, text

app = Flask(__name__)
CORS(app, 
     resources={r"/*": {
         "origins": "*",
         "supports_credentials": True
     }})

# Configuración
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tu_clave_secreta_aqui')

# Configuración de la base de datos para Render
print("Configurando conexión a la base de datos...")
database_url = os.environ.get('DATABASE_URL')

if database_url:
    print(f"URL de base de datos encontrada, comienza con: postgresql...")
    try:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
            print("URL convertida de postgres:// a postgresql://")
        
        if not database_url.startswith("postgresql://"):
            raise ValueError("La URL de la base de datos debe comenzar con postgresql://")
            
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        database_url = 'sqlite:///' + os.path.join(basedir, 'autism_learning.db')
else:
    print("No se encontró URL de base de datos, usando SQLite")
    database_url = 'sqlite:///' + os.path.join(basedir, 'autism_learning.db')

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Inicializar extensiones
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelos
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    profile_photo = db.Column(db.String(500), default='https://i.pravatar.cc/300')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, default=0)
    percentage = db.Column(db.Float, default=0.0)
    completed_cards = db.Column(db.Integer, default=0)
    total_cards = db.Column(db.Integer, default=3)
    completed = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, user_id, category, score=0, percentage=0.0, completed_cards=0, completed=False):
        self.user_id = user_id
        self.category = category
        self.score = score
        self.percentage = percentage
        self.completed_cards = completed_cards
        self.completed = completed
        self.updated_at = datetime.utcnow()

class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    question = db.Column(db.String(500), nullable=False)
    image_url = db.Column(db.String(500))
    options = db.Column(db.String(1000), nullable=False)  # JSON string of options
    correct_option = db.Column(db.Integer, nullable=False)
    feedback = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rutas de autenticación
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['name', 'email', 'password']):
            return jsonify({'error': 'Faltan datos requeridos'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'El correo electrónico ya está registrado'}), 400
        
        new_user = User(
            name=data['name'],
            email=data['email']
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'message': 'Usuario registrado exitosamente'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template_string(HTML_TEMPLATE)
        
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()

        if not all(k in data for k in ['email', 'password']):
            return jsonify({'error': 'Faltan datos requeridos'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
            
        if not user.check_password(data['password']):
            return jsonify({'error': 'Contraseña incorrecta'}), 401
            
        login_user(user)
        return jsonify({'message': 'Login exitoso', 'redirect': url_for('dashboard')}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/save-progress', methods=['POST'])
@login_required
def save_progress():
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['category', 'score', 'percentage']):
            return jsonify({'error': 'Faltan datos requeridos'}), 400

        # Buscar progreso existente
        progress = UserProgress.query.filter_by(
            user_id=current_user.id,
            category=data['category']
        ).first()

        if not progress:
            # Crear nuevo registro si no existe
            progress = UserProgress(
                user_id=current_user.id,
                category=data['category']
            )
            db.session.add(progress)

        # Actualizar el progreso
        progress.score = max(progress.score, int(data['score']))
        progress.percentage = max(progress.percentage, float(data['percentage']))
        progress.completed_cards = int((float(data['percentage']) / 100) * 3)  # 3 cards per category
        progress.completed = data.get('completed', False)
        progress.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Progreso guardado exitosamente',
            'progress': {
                'score': progress.score,
                'percentage': progress.percentage,
                'completed_cards': progress.completed_cards,
                'completed': progress.completed
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error saving progress: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get-progress/<category>')
@login_required
def get_progress(category):
    try:
        progress = UserProgress.query.filter_by(
            user_id=current_user.id,
            category=category
        ).order_by(UserProgress.updated_at.desc()).first()
        
        if progress:
            return jsonify({
                'score': progress.score,
                'percentage': progress.percentage,
                'completed': progress.completed
            })
        return jsonify({
            'score': 0,
            'percentage': 0,
            'completed': False
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/dashboard')
@login_required
def dashboard():
    categories = {
        'emociones': {
            'name': 'Desarrollo Emocional',
            'icon': '😊',
            'color': '#FF9800',
            'description': 'Aprende sobre emociones y expresiones faciales'
        },
        'conceptos': {
            'name': 'Conceptos Básicos',
            'icon': '📚',
            'color': '#4CAF50',
            'description': 'Aprende formas, colores y números'
        },
        'entorno': {
            'name': 'Conocimiento del Entorno',
            'icon': '🌍',
            'color': '#2196F3',
            'description': 'Aprende sobre animales, clima y naturaleza'
        }
    }
    
    study_fields = []
    for key, category in categories.items():
        # Obtener el progreso más reciente
        progress = UserProgress.query.filter_by(
            user_id=current_user.id,
            category=key
        ).first()
        
        study_fields.append({
            'name': category['name'],
            'route': key,
            'icon': category['icon'],
            'color': category['color'],
            'description': category['description'],
            'progress': progress.percentage if progress else 0,
            'completed_cards': progress.completed_cards if progress else 0,
            'total_cards': 3,  # Total de tarjetas por categoría
            'completed': progress.completed if progress else False
        })

    return render_template_string(
        DASHBOARD_TEMPLATE,
        study_fields=study_fields,
        current_user=current_user
    )

@app.route('/profile')
@login_required
def profile():
    return render_template_string(PROFILE_TEMPLATE, current_user=current_user)

@app.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    try:
        user = User.query.get(current_user.id)
        
        user.name = request.form.get('name', user.name)
        user.email = request.form.get('email', user.email)
        user.profile_photo = request.form.get('profile_photo', user.profile_photo)
        
        if request.form.get('password'):
            user.set_password(request.form.get('password'))
        
        db.session.commit()
        return redirect(url_for('profile'))
    except Exception as e:
        db.session.rollback()
        return str(e), 500

@app.route('/progress')
@login_required
def progress():
    categories = {
        'emociones': {
            'name': 'Desarrollo Emocional',
            'icon': '😊',
            'color': '#FF9800'
        },
        'conceptos': {
            'name': 'Conceptos Básicos',
            'icon': '📚',
            'color': '#4CAF50'
        },
        'entorno': {
            'name': 'Conocimiento del Entorno',
            'icon': '🌍',
            'color': '#2196F3'
        }
    }
    
    progress_data = []
    for category_key, category in categories.items():
        try:
            # Obtener todos los registros de progreso para esta categoría
            progress_records = UserProgress.query.filter_by(
                user_id=current_user.id,
                category=category_key
            ).order_by(UserProgress.updated_at.desc()).all()
            
            # Calcular estadísticas
            completed_cards = len([p for p in progress_records if p.completed])
            best_score = max([p.score for p in progress_records]) if progress_records else 0
            last_activity = progress_records[0].updated_at.strftime('%d/%m/%Y') if progress_records else 'Sin actividad'
            
            # Calcular el progreso total basado en el mejor score
            try:
                total_progress = max([p.percentage for p in progress_records]) if progress_records else 0
            except:
                total_progress = (best_score / 3.0) * 100 if best_score > 0 else 0
            
            progress_data.append({
                'name': category['name'],
                'icon': category['icon'],
                'color': category['color'],
                'completed_cards': completed_cards,
                'total_cards': 3,  # Total de tarjetas por categoría
                'best_score': best_score,
                'last_activity': last_activity,
                'progress': total_progress
            })
        except Exception as e:
            print(f"Error processing progress for {category_key}: {str(e)}")
            # Agregar datos por defecto si hay error
            progress_data.append({
                'name': category['name'],
                'icon': category['icon'],
                'color': category['color'],
                'completed_cards': 0,
                'total_cards': 3,
                'best_score': 0,
                'last_activity': 'Sin actividad',
                'progress': 0
            })
    
    return render_template_string(PROGRESS_TEMPLATE, progress_data=progress_data, current_user=current_user)

@app.route('/get-all-progress')
@login_required
def get_all_progress():
    try:
        progress_data = {}
        categories = ['emociones', 'conceptos', 'entorno']
        
        for category in categories:
            progress = UserProgress.query.filter_by(
                user_id=current_user.id,
                category=category
            ).first()
            
            if progress:
                progress_data[category] = {
                    'score': progress.score,
                    'percentage': progress.percentage,
                    'completed_cards': progress.completed_cards,
                    'completed': progress.completed,
                    'last_activity': progress.updated_at.strftime('%d/%m/%Y')
                }
            else:
                progress_data[category] = {
                    'score': 0,
                    'percentage': 0,
                    'completed_cards': 0,
                    'completed': False,
                    'last_activity': 'Sin actividad'
                }
        
        return jsonify(progress_data)
    except Exception as e:
        print(f"Error getting progress: {str(e)}")
        return jsonify({'error': str(e)}), 500

def init_flashcards():
    default_cards = {
        'emociones': [
            {
                'question': '¿Cómo te sientes cuando ves esta cara?',
                'image_url': 'https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Grinning%20face/3D/grinning_face_3d.png',
                'options': ['Feliz', 'Triste', 'Enojado', 'Asustado'],
                'correct_option': 0,
                'feedback': '¡Muy bien! Cuando alguien sonríe así, está feliz y contento.'
            },
            {
                'question': '¿Qué emoción muestra esta cara?',
                'image_url': 'https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Crying%20face/3D/crying_face_3d.png',
                'options': ['Triste', 'Feliz', 'Sorprendido', 'Enojado'],
                'correct_option': 0,
                'feedback': '¡Correcto! Es importante reconocer cuando alguien está triste para poder ayudar.'
            },
            {
                'question': '¿Qué emoción expresa esta cara?',
                'image_url': 'https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Angry%20face/3D/angry_face_3d.png',
                'options': ['Enojado', 'Feliz', 'Triste', 'Asustado'],
                'correct_option': 0,
                'feedback': '¡Excelente! Reconocer cuando alguien está enojado nos ayuda a entender sus sentimientos.'
            }
        ],
        'conceptos': [
            {
                'question': '¿Qué número viene después del 2?',
                'image_url': 'https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Keycap%203/3D/keycap_3_3d.png',
                'options': ['3', '4', '2', '1'],
                'correct_option': 0,
                'feedback': '¡Excelente! El número 3 viene después del 2. ¡Estás aprendiendo a contar muy bien!'
            },
            {
                'question': '¿Cuál es el primer número?',
                'image_url': 'https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Keycap%201/3D/keycap_1_3d.png',
                'options': ['1', '2', '3', '4'],
                'correct_option': 0,
                'feedback': '¡Correcto! El número 1 es el primero que usamos para contar. ¡Muy bien hecho!'
            },
            {
                'question': '¿Qué número está entre el 1 y el 3?',
                'image_url': 'https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Keycap%202/3D/keycap_2_3d.png',
                'options': ['2', '4', '1', '3'],
                'correct_option': 0,
                'feedback': '¡Perfecto! El número 2 está entre el 1 y el 3. ¡Eres muy inteligente!'
            }
        ],
        'entorno': [
            {
                'question': '¿Qué animal es este?',
                'image_url': 'https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Dog%20face/3D/dog_face_3d.png',
                'options': ['Perro', 'Gato', 'Conejo', 'Pájaro'],
                'correct_option': 0,
                'feedback': '¡Correcto! Es un perro, un animal doméstico muy común.'
            },
            {
                'question': '¿Qué clima representa esta imagen?',
                'image_url': 'https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Sun/3D/sun_3d.png',
                'options': ['Soleado', 'Lluvioso', 'Nublado', 'Nevado'],
                'correct_option': 0,
                'feedback': '¡Muy bien! Es un día soleado.'
            },
            {
                'question': '¿Qué fruta es esta?',
                'image_url': 'https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Red%20apple/3D/red_apple_3d.png',
                'options': ['Manzana', 'Naranja', 'Plátano', 'Pera'],
                'correct_option': 0,
                'feedback': '¡Excelente! Es una manzana roja.'
            }
        ]
    }

    for category, cards in default_cards.items():
        for card in cards:
            existing_card = Flashcard.query.filter_by(
                category=category,
                question=card['question']
            ).first()
            
            if not existing_card:
                new_card = Flashcard(
                    category=category,
                    question=card['question'],
                    image_url=card['image_url'],
                    options=str(card['options']),
                    correct_option=card['correct_option'],
                    feedback=card['feedback']
                )
                db.session.add(new_card)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error initializing flashcards: {e}")

@app.route('/api/flashcards/<category>')
@login_required
def get_flashcards(category):
    try:
        cards = Flashcard.query.filter_by(category=category).all()
        if not cards:
            return jsonify({'error': 'No se encontraron flashcards para esta categoría'}), 404
            
        return jsonify([{
            'id': card.id,
            'question': card.question,
            'image_url': card.image_url,
            'options': eval(card.options),
            'correct_option': card.correct_option,
            'feedback': card.feedback
        } for card in cards])
    except Exception as e:
        print(f"Error getting flashcards: {e}")
        return jsonify({'error': 'Error al obtener las flashcards'}), 500

def init_db():
    print("Iniciando inicialización de la base de datos...")
    try:
        # Crear todas las tablas
        print("Creando tablas de la base de datos...")
        db.create_all()
        print("Tablas creadas correctamente")
        
        # Verificar si necesitamos inicializar datos
        user_count = User.query.count()
        print(f"Número de usuarios existentes: {user_count}")
        
        if user_count == 0:
            print("Inicializando flashcards...")
            init_flashcards()
            print("Flashcards inicializadas correctamente")
        return True
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
        return False

# Inicializar la base de datos al arrancar la aplicación
with app.app_context():
    print("Iniciando la aplicación - Configuración inicial de la base de datos...")
    init_db()

if __name__ == '__main__':
    app.run(debug=True) 