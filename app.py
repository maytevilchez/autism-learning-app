from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

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
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///' + os.path.join(basedir, 'autism_learning.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Template HTML para la página de inicio
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sistema de Aprendizaje</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Poppins', sans-serif;
        }

        body {
            min-height: 100vh;
            background: #E3F2FD;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .auth-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
            overflow: hidden;
            width: 100%;
            max-width: 900px;
            display: flex;
        }

        .auth-form {
            padding: 40px;
            width: 50%;
            background: white;
        }

        .auth-info {
            padding: 40px;
            width: 50%;
            background: #0091FF;
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }

        h1 {
            color: #0091FF;
            font-size: 2em;
            margin-bottom: 30px;
            font-weight: 600;
        }

        .form-group {
            margin-bottom: 25px;
        }

        input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e1e1e1;
            border-radius: 10px;
            font-size: 1em;
            transition: all 0.3s ease;
        }

        input:focus {
            outline: none;
            border-color: #0091FF;
            box-shadow: 0 0 0 3px rgba(0, 145, 255, 0.1);
        }

        button {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 10px;
            background: #0091FF;
            color: white;
            font-size: 1em;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        button:hover {
            background: #007acc;
            transform: translateY(-2px);
        }

        @media (max-width: 768px) {
            .auth-container {
                flex-direction: column;
            }

            .auth-form, .auth-info {
                width: 100%;
            }
        }

        .error-message {
            color: #e74c3c;
            background: #ffd7d7;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
            display: none;
        }
        .success-message {
            color: #27ae60;
            background: #d4ffda;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="auth-container" id="authContainer">
        <!-- Formulario de Login -->
        <div class="auth-form" id="loginForm">
            <h1>Iniciar Sesión</h1>
            <div class="error-message" id="loginError"></div>
            <div class="success-message" id="loginSuccess"></div>
            <form onsubmit="handleLogin(event)">
                <div class="form-group">
                    <input type="email" name="email" required placeholder="Correo Electrónico">
                </div>
                <div class="form-group">
                    <input type="password" name="password" required placeholder="Contraseña">
                </div>
                <button type="submit">Entrar</button>
            </form>
        </div>
        
        <!-- Información adicional -->
        <div class="auth-info">
            <h2>¿Aún no tienes una cuenta?</h2>
            <p>Regístrate para que puedas iniciar sesión</p>
            <a href="#" class="switch-form" onclick="toggleForms()">Registrarse</a>
        </div>

        <!-- Formulario de Registro -->
        <div class="auth-form" id="registerForm" style="display: none;">
            <h1>Registro</h1>
            <div class="error-message" id="registerError"></div>
            <div class="success-message" id="registerSuccess"></div>
            <form onsubmit="handleRegister(event)">
                <div class="form-group">
                    <input type="text" name="name" required placeholder="Nombre Completo">
                </div>
                <div class="form-group">
                    <input type="email" name="email" required placeholder="Correo Electrónico">
                </div>
                <div class="form-group">
                    <input type="password" name="password" required placeholder="Contraseña">
                </div>
                <button type="submit">Registrarse</button>
            </form>
        </div>
    </div>

    <script>
        let isLoginForm = true;

        function toggleForms() {
            const loginForm = document.getElementById('loginForm');
            const registerForm = document.getElementById('registerForm');
            const authInfo = document.querySelector('.auth-info');

            if (isLoginForm) {
                loginForm.style.display = 'none';
                registerForm.style.display = 'block';
                authInfo.innerHTML = `
                    <h2>¿Ya tienes una cuenta?</h2>
                    <p>Inicia sesión para continuar aprendiendo</p>
                    <a href="#" class="switch-form" onclick="toggleForms()">Iniciar Sesión</a>
                `;
            } else {
                loginForm.style.display = 'block';
                registerForm.style.display = 'none';
                authInfo.innerHTML = `
                    <h2>¿Aún no tienes una cuenta?</h2>
                    <p>Regístrate para que puedas iniciar sesión</p>
                    <a href="#" class="switch-form" onclick="toggleForms()">Registrarse</a>
                `;
            }
            isLoginForm = !isLoginForm;
        }

        async function handleLogin(event) {
            event.preventDefault();
            const form = event.target;
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    document.getElementById('loginSuccess').style.display = 'block';
                    document.getElementById('loginSuccess').textContent = '¡Inicio de sesión exitoso!';
                    window.location.href = '/dashboard';
                } else {
                    const error = await response.json();
                    document.getElementById('loginError').style.display = 'block';
                    document.getElementById('loginError').textContent = error.error || 'Error al iniciar sesión';
                }
            } catch (error) {
                document.getElementById('loginError').style.display = 'block';
                document.getElementById('loginError').textContent = 'Error de conexión';
            }
        }

        async function handleRegister(event) {
            event.preventDefault();
            const form = event.target;
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    document.getElementById('registerSuccess').style.display = 'block';
                    document.getElementById('registerSuccess').textContent = '¡Registro exitoso! Redirigiendo...';
                    setTimeout(() => {
                        toggleForms();
                    }, 2000);
                } else {
                    const error = await response.json();
                    document.getElementById('registerError').style.display = 'block';
                    document.getElementById('registerError').textContent = error.error || 'Error al registrarse';
                }
            } catch (error) {
                document.getElementById('registerError').style.display = 'block';
                document.getElementById('registerError').textContent = 'Error de conexión';
            }
        }
    </script>
</body>
</html>
"""

# Template para el Dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - Sistema de Aprendizaje</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Poppins', sans-serif;
        }

        body {
            min-height: 100vh;
            background: #E3F2FD;
            display: flex;
        }

        .sidebar {
            width: 280px;
            background: white;
            padding: 30px;
            display: flex;
            flex-direction: column;
            border-right: 1px solid #e1e1e1;
            position: fixed;
            height: 100vh;
        }

        .profile-section {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            border-bottom: 1px solid #e1e1e1;
        }

        .profile-photo {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            margin-bottom: 15px;
            object-fit: cover;
            border: 3px solid #0091FF;
        }

        .user-name {
            font-size: 1.5em;
            color: #2d3748;
            margin-bottom: 5px;
        }

        .user-email {
            color: #718096;
            font-size: 0.9em;
        }

        .nav-menu {
            list-style: none;
            margin-top: 20px;
        }

        .nav-item {
            margin-bottom: 15px;
        }

        .nav-link {
            display: flex;
            align-items: center;
            padding: 12px 15px;
            color: #2d3748;
            text-decoration: none;
            border-radius: 10px;
            transition: all 0.3s ease;
        }

        .nav-link:hover {
            background: #E3F2FD;
            color: #0091FF;
        }

        .nav-link.active {
            background: #0091FF;
            color: white;
        }

        .main-content {
            flex: 1;
            margin-left: 280px;
            padding: 30px;
        }

        .section-title {
            font-size: 2em;
            color: #2d3748;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 2px solid #0091FF;
        }

        .study-fields {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
        }

        .field-card {
            background: white;
            border-radius: 20px;
            padding: 25px;
            transition: all 0.3s ease;
            cursor: pointer;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            position: relative;
            overflow: hidden;
        }

        .field-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 5px;
            background: var(--card-color);
        }

        .field-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
        }

        .field-icon {
            font-size: 2.5em;
            margin-bottom: 15px;
            color: var(--card-color);
        }

        .field-title {
            font-size: 1.3em;
            color: #2d3748;
            font-weight: 600;
            margin-bottom: 10px;
        }

        .field-description {
            color: #718096;
            font-size: 0.9em;
            margin-bottom: 20px;
            line-height: 1.5;
        }

        .progress-bar {
            height: 15px;
            background: #E2E8F0;
            border-radius: 8px;
            overflow: hidden;
            margin: 15px 0;
        }

        .progress-fill {
            height: 100%;
            background: var(--card-color);
            border-radius: 8px;
            transition: width 0.5s ease;
        }

        .progress-text {
            display: flex;
            justify-content: space-between;
            color: #718096;
            font-size: 0.9em;
            font-weight: 500;
        }

        .logout-btn {
            margin-top: auto;
            padding: 12px 20px;
            background: #e53e3e;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .logout-btn:hover {
            background: #c53030;
        }

        @media (max-width: 768px) {
            .sidebar {
                width: 100%;
                height: auto;
                position: relative;
                border-right: none;
                border-bottom: 1px solid #e1e1e1;
            }

            .main-content {
                margin-left: 0;
            }

            .study-fields {
                grid-template-columns: 1fr;
            }
        }

        .flashcards-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            padding: 2rem;
        }

        .flashcard {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 1.5rem;
            position: relative;
            transition: transform 0.3s ease;
        }

        .flashcard:hover {
            transform: translateY(-5px);
        }

        .flashcard img {
            width: 200px;
            height: 200px;
            object-fit: contain;
            border-radius: 10px;
            transition: all 0.3s ease;
        }

        .flashcard h3 {
            font-size: 1.2rem;
            text-align: center;
            color: #333;
            margin: 0;
            padding: 1rem;
        }

        .flashcard .options {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            width: 100%;
        }

        .flashcard .options button {
            padding: 1rem;
            border: 2px solid #e1e1e1;
            border-radius: 10px;
            background: white;
            color: #333;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .flashcard .options button:hover {
            background: #f0f0f0;
            border-color: #ccc;
            transform: translateY(-2px);
        }

        .flashcard .options button.correct {
            background: #4CAF50;
            color: white;
            border-color: #4CAF50;
        }

        .flashcard .options button.incorrect {
            background: #f44336;
            color: white;
            border-color: #f44336;
        }

        .flashcard .feedback {
            display: none;
            position: absolute;
            bottom: -60px;
            left: 0;
            right: 0;
            background: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            animation: slideUp 0.3s ease forwards;
        }

        .flashcard .feedback.correct {
            background: #4CAF50;
            color: white;
        }

        .flashcard .feedback.incorrect {
            background: #f44336;
            color: white;
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .progress-indicator {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 1rem;
            margin: 2rem 0;
        }

        .progress-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #e1e1e1;
            transition: all 0.3s ease;
        }

        .progress-dot.active {
            background: #0091FF;
            transform: scale(1.2);
        }

        .progress-dot.completed {
            background: #4CAF50;
        }

        .navigation-buttons {
            display: flex;
            justify-content: space-between;
            margin-top: 2rem;
            padding: 0 2rem;
        }

        .nav-button {
            padding: 1rem 2rem;
            border: none;
            border-radius: 10px;
            background: #0091FF;
            color: white;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .nav-button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }

        .nav-button:hover:not(:disabled) {
            background: #007acc;
            transform: translateY(-2px);
        }

        .completion-message {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            text-align: center;
            z-index: 1000;
            animation: fadeIn 0.5s ease;
        }

        .completion-message h2 {
            color: #4CAF50;
            margin-bottom: 1rem;
            font-size: 1.8rem;
        }

        .completion-message p {
            color: #666;
            margin-bottom: 1.5rem;
        }

        .completion-message button {
            padding: 1rem 2rem;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.3s ease;
        }

        .completion-message button:hover {
            background: #388E3C;
            transform: translateY(-2px);
        }

        .overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 999;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translate(-50%, -60%);
            }
            to {
                opacity: 1;
                transform: translate(-50%, -50%);
            }
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="profile-section">
            <img src="{{ current_user.profile_photo }}" alt="Profile Photo" class="profile-photo">
            <h2 class="user-name">{{ current_user.name }}</h2>
            <p class="user-email">{{ current_user.email }}</p>
        </div>
        <ul class="nav-menu">
            <li class="nav-item">
                <a href="/dashboard" class="nav-link active">
                    📊 Dashboard
                </a>
            </li>
            <li class="nav-item">
                <a href="/profile" class="nav-link">
                    👤 Mi Perfil
                </a>
            </li>
            <li class="nav-item">
                <a href="/progress" class="nav-link">
                    📈 Mi Progreso
                </a>
            </li>
        </ul>
        <a href="/logout" class="logout-btn">Cerrar Sesión</a>
    </div>

    <div class="main-content">
        <button id="backButton" class="back-button" onclick="showDashboard()">
            ← Volver a Campos de Estudio
        </button>
        
        <div id="dashboardView">
            <h1 class="section-title">Campo de Estudio</h1>
            <div class="study-fields">
                {% for field in study_fields %}
                <div class="field-card" 
                    onclick="loadFlashcards('{{ field.route }}')"
                    style="--card-color: {{ field.color }}"
                    data-category="{{ field.route }}">
                    <div class="field-icon">{{ field.icon }}</div>
                    <h3 class="field-title">{{ field.name }}</h3>
                    <p class="field-description">{{ field.description }}</p>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {{ field.progress }}%"></div>
                    </div>
                    <div class="progress-text">
                        <span>Progreso</span>
                        <span class="progress-percentage">{{ "%.0f"|format(field.progress) }}%</span>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <div id="flashcardsView" style="display: none;">
            <h2 id="categoryTitle" class="section-title"></h2>
            <div class="progress-indicator" id="progressIndicator"></div>
            <div id="flashcardsContainer" class="flashcards-container"></div>
            <div class="navigation-buttons">
                <button id="prevButton" class="nav-button" onclick="previousCard()" disabled>← Anterior</button>
                <button id="nextButton" class="nav-button" onclick="nextCard()">Siguiente →</button>
            </div>
        </div>
    </div>

    <div class="overlay" id="overlay"></div>
    <div class="completion-message" id="completionMessage">
        <h2>¡Felicitaciones! 🎉</h2>
        <p>Has completado todas las tarjetas de esta categoría</p>
        <p id="finalScore"></p>
        <button onclick="returnToDashboard()">Volver al Dashboard</button>
    </div>

    <script>
        let currentCardIndex = 0;
        let currentFlashcards = [];
        let answeredCards = new Set();
        let correctAnswers = 0;
        let currentCategory = '';

        function showDashboard() {
            document.getElementById('dashboardView').style.display = 'block';
            document.getElementById('flashcardsView').style.display = 'none';
            document.getElementById('backButton').style.display = 'none';
            document.getElementById('overlay').style.display = 'none';
            document.getElementById('completionMessage').style.display = 'none';
            // Reset state
            currentCardIndex = 0;
            currentFlashcards = [];
            answeredCards.clear();
            correctAnswers = 0;
        }

        function showFlashcards() {
            document.getElementById('dashboardView').style.display = 'none';
            document.getElementById('flashcardsView').style.display = 'block';
            document.getElementById('backButton').style.display = 'block';
        }

        function updateProgressDots() {
            const progressIndicator = document.getElementById('progressIndicator');
            progressIndicator.innerHTML = '';
            
            currentFlashcards.forEach((_, index) => {
                const dot = document.createElement('div');
                dot.className = 'progress-dot';
                if (index === currentCardIndex) dot.className += ' active';
                if (answeredCards.has(index)) {
                    dot.className += ' completed';
                }
                progressIndicator.appendChild(dot);
            });
        }

        function updateNavigationButtons() {
            const prevButton = document.getElementById('prevButton');
            const nextButton = document.getElementById('nextButton');
            
            prevButton.disabled = currentCardIndex === 0;
            
            if (currentCardIndex === currentFlashcards.length - 1) {
                nextButton.textContent = 'Finalizar';
                nextButton.disabled = !answeredCards.has(currentCardIndex);
            } else {
                nextButton.textContent = 'Siguiente →';
                nextButton.disabled = !answeredCards.has(currentCardIndex);
            }
        }

        function previousCard() {
            if (currentCardIndex > 0) {
                currentCardIndex--;
                displayCurrentCard();
            }
        }

        function nextCard() {
            if (currentCardIndex < currentFlashcards.length - 1) {
                currentCardIndex++;
                displayCurrentCard();
            } else if (answeredCards.size === currentFlashcards.length) {
                const percentage = (correctAnswers / currentFlashcards.length) * 100;
                showCompletionMessage(correctAnswers, percentage);
            }
        }

        function displayCurrentCard() {
            const container = document.getElementById('flashcardsContainer');
            const card = currentFlashcards[currentCardIndex];
            
            container.innerHTML = `
                <div class="flashcard">
                    <img src="${card.image_url}" alt="${card.question}">
                    <h3>${card.question}</h3>
                    <div class="options">
                        ${card.options.map((option, index) => `
                            <button onclick="checkAnswer(${index}, ${card.correct_option}, '${card.feedback}')"
                                    ${answeredCards.has(currentCardIndex) ? 'disabled' : ''}>
                                ${option}
                            </button>
                        `).join('')}
                    </div>
                    <div class="feedback"></div>
                </div>
            `;
            
            updateProgressDots();
            updateNavigationButtons();
        }

        async function loadFlashcards(category) {
            try {
                currentCategory = category;
                const response = await fetch(`/api/flashcards/${category}`);
                currentFlashcards = await response.json();
                
                // Reset state
                currentCardIndex = 0;
                answeredCards.clear();
                correctAnswers = 0;
                
                // Set category title
                const titles = {
                    'emociones': 'Desarrollo Emocional',
                    'conceptos': 'Conceptos Básicos',
                    'entorno': 'Conocimiento del Entorno'
                };
                document.getElementById('categoryTitle').textContent = titles[category];
                
                displayCurrentCard();
                showFlashcards();

                // Cargar progreso existente
                await loadExistingProgress(category);
            } catch (error) {
                console.error('Error loading flashcards:', error);
                alert('Error al cargar las tarjetas de aprendizaje');
            }
        }

        async function loadExistingProgress(category) {
            try {
                const response = await fetch('/get-all-progress');
                const progressData = await response.json();
                
                if (progressData[category]) {
                    const progress = progressData[category];
                    // Restaurar el estado de progreso
                    correctAnswers = progress.score;
                    const completedCount = Math.floor((progress.percentage / 100) * currentFlashcards.length);
                    
                    // Marcar las tarjetas como completadas
                    for (let i = 0; i < completedCount; i++) {
                        answeredCards.add(i);
                    }
                    
                    updateProgressDots();
                    updateNavigationButtons();
                }
            } catch (error) {
                console.error('Error loading progress:', error);
            }
        }

        async function saveProgress(category, score, percentage, completed) {
            try {
                const response = await fetch('/save-progress', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        category: category,
                        score: score,
                        percentage: percentage,
                        completed: completed
                    })
                });

                if (!response.ok) {
                    throw new Error('Error al guardar el progreso');
                }

                const result = await response.json();
                console.log('Progreso guardado:', result);

                // Actualizar el dashboard después de guardar el progreso
                await updateDashboardProgress();

                // Mostrar mensaje de completado si corresponde
                if (completed) {
                    showCompletionMessage(score, percentage);
                }

                // Actualizar la barra de progreso en la tarjeta actual
                updateProgressUI(category, percentage);
            } catch (error) {
                console.error('Error saving progress:', error);
            }
        }

        function updateProgressUI(category, percentage) {
            const currentCard = document.querySelector(`[data-category="${category}"]`);
            if (currentCard) {
                const progressBar = currentCard.querySelector('.progress-fill');
                const progressText = currentCard.querySelector('.progress-percentage');
                if (progressBar && progressText) {
                    progressBar.style.width = `${percentage}%`;
                    progressText.textContent = `${Math.round(percentage)}%`;
                }
            }
        }

        function showCompletionMessage(score, percentage) {
            const finalScoreText = document.getElementById('finalScore');
            if (finalScoreText) {
                finalScoreText.textContent = `¡Has completado ${Math.round(percentage)}% con ${score} respuestas correctas!`;
            }
            document.getElementById('overlay').style.display = 'block';
            document.getElementById('completionMessage').style.display = 'block';
        }

        function checkAnswer(selectedIndex, correctIndex, feedback) {
            if (answeredCards.has(currentCardIndex)) {
                return; // Evitar responder múltiples veces la misma tarjeta
            }

            const isCorrect = selectedIndex === correctIndex;
            const options = document.querySelectorAll('.flashcard .options button');
            const feedbackElement = document.querySelector('.flashcard .feedback');
            
            if (isCorrect) {
                correctAnswers++;
            }
            answeredCards.add(currentCardIndex);
            
            // Calcular y guardar progreso
            const totalCards = currentFlashcards.length;
            const percentage = (answeredCards.size / totalCards) * 100;
            
            // Guardar en el backend y actualizar UI
            saveProgress(
                currentCategory,
                correctAnswers,
                percentage,
                answeredCards.size === totalCards
            );
            
            options.forEach(button => button.disabled = true);
            options[selectedIndex].className = isCorrect ? 'correct' : 'incorrect';
            options[correctIndex].className = 'correct';
            
            feedbackElement.textContent = isCorrect ? `¡Correcto! ${feedback}` : 'Incorrecto, intenta de nuevo';
            feedbackElement.className = `feedback ${isCorrect ? 'correct' : 'incorrect'}`;
            feedbackElement.style.display = 'block';
            
            updateProgressDots();
            updateNavigationButtons();
        }

        async function updateDashboardProgress() {
            try {
                const response = await fetch('/get-all-progress');
                const progressData = await response.json();
                
                Object.entries(progressData).forEach(([category, data]) => {
                    const card = document.querySelector(`[data-category="${category}"]`);
                    if (card) {
                        const progressBar = card.querySelector('.progress-fill');
                        const progressText = card.querySelector('.progress-percentage');
                        if (progressBar && progressText) {
                            progressBar.style.width = `${data.percentage}%`;
                            progressText.textContent = `${Math.round(data.percentage)}%`;
                        }
                    }
                });
            } catch (error) {
                console.error('Error updating dashboard:', error);
            }
        }

        // Actualizar el progreso cuando se carga la página
        document.addEventListener('DOMContentLoaded', updateDashboardProgress);

        function returnToDashboard() {
            window.location.href = '/dashboard';
        }
    </script>
</body>
</html>
"""

# Template para la página de perfil
PROFILE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mi Perfil - Sistema de Aprendizaje</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* Reutilizar los estilos base del dashboard */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Poppins', sans-serif;
        }

        body {
            min-height: 100vh;
            background: #E3F2FD;
            display: flex;
        }

        .sidebar {
            width: 280px;
            background: white;
            padding: 30px;
            display: flex;
            flex-direction: column;
            border-right: 1px solid #e1e1e1;
            position: fixed;
            height: 100vh;
        }

        .profile-section {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            border-bottom: 1px solid #e1e1e1;
        }

        .profile-photo {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            margin-bottom: 15px;
            object-fit: cover;
            border: 3px solid #0091FF;
        }

        .user-name {
            font-size: 1.5em;
            color: #2d3748;
            margin-bottom: 5px;
        }

        .user-email {
            color: #718096;
            font-size: 0.9em;
        }

        .nav-menu {
            list-style: none;
            margin-top: 20px;
        }

        .nav-item {
            margin-bottom: 15px;
        }

        .nav-link {
            display: flex;
            align-items: center;
            padding: 12px 15px;
            color: #2d3748;
            text-decoration: none;
            border-radius: 10px;
            transition: all 0.3s ease;
        }

        .nav-link:hover {
            background: #E3F2FD;
            color: #0091FF;
        }

        .nav-link.active {
            background: #0091FF;
            color: white;
        }

        .main-content {
            flex: 1;
            margin-left: 280px;
            padding: 30px;
        }

        .section-title {
            font-size: 2em;
            color: #2d3748;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 2px solid #0091FF;
        }

        .profile-card {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .profile-form {
            display: grid;
            gap: 20px;
            max-width: 600px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .form-group label {
            color: #2d3748;
            font-weight: 500;
        }

        .avatar-selector {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
            gap: 1rem;
            margin-top: 0.5rem;
        }

        .avatar-option {
            cursor: pointer;
            border: 3px solid transparent;
            border-radius: 50%;
            padding: 2px;
            transition: all 0.3s ease;
        }

        .avatar-option:hover {
            transform: scale(1.1);
        }

        .avatar-option.selected {
            border-color: #0091FF;
        }

        .avatar-option img {
            width: 100%;
            height: auto;
            border-radius: 50%;
        }

        .form-group input {
            padding: 12px;
            border: 2px solid #e1e1e1;
            border-radius: 10px;
            font-size: 1em;
            transition: all 0.3s ease;
        }

        .form-group input:focus {
            outline: none;
            border-color: #0091FF;
            box-shadow: 0 0 0 3px rgba(0, 145, 255, 0.1);
        }

        .save-btn {
            padding: 12px 24px;
            background: #0091FF;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .save-btn:hover {
            background: #007acc;
        }

        .logout-btn {
            margin-top: auto;
            padding: 12px 20px;
            background: #e53e3e;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            text-align: center;
        }

        .logout-btn:hover {
            background: #c53030;
        }

        @media (max-width: 768px) {
            .sidebar {
                width: 100%;
                height: auto;
                position: relative;
                border-right: none;
                border-bottom: 1px solid #e1e1e1;
            }

            .main-content {
                margin-left: 0;
            }
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="profile-section">
            <img src="{{ current_user.profile_photo }}" alt="Profile Photo" class="profile-photo">
            <h2 class="user-name">{{ current_user.name }}</h2>
            <p class="user-email">{{ current_user.email }}</p>
        </div>
        <ul class="nav-menu">
            <li class="nav-item">
                <a href="/dashboard" class="nav-link">
                    📊 Dashboard
                </a>
            </li>
            <li class="nav-item">
                <a href="/profile" class="nav-link active">
                    👤 Mi Perfil
                </a>
            </li>
            <li class="nav-item">
                <a href="/progress" class="nav-link">
                    📈 Mi Progreso
                </a>
            </li>
        </ul>
        <a href="/logout" class="logout-btn">Cerrar Sesión</a>
    </div>

    <div class="main-content">
        <h1 class="section-title">Mi Perfil</h1>
        <div class="profile-card">
            <form class="profile-form" action="/update-profile" method="POST">
                <div class="form-group">
                    <label for="name">Nombre Completo</label>
                    <input type="text" id="name" name="name" value="{{ current_user.name }}" required>
                </div>
                <div class="form-group">
                    <label for="email">Correo Electrónico</label>
                    <input type="email" id="email" name="email" value="{{ current_user.email }}" required>
                </div>
                <div class="form-group">
                    <label>Selecciona tu Avatar</label>
                    <input type="hidden" id="profile_photo" name="profile_photo" value="{{ current_user.profile_photo }}">
                    <div class="avatar-selector">
                        <div class="avatar-option" onclick="selectAvatar('https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Grinning%20face/3D/grinning_face_3d.png')">
                            <img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Grinning%20face/3D/grinning_face_3d.png" alt="Avatar 1">
                        </div>
                        <div class="avatar-option" onclick="selectAvatar('https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Smiling%20face%20with%20hearts/3D/smiling_face_with_hearts_3d.png')">
                            <img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Smiling%20face%20with%20hearts/3D/smiling_face_with_hearts_3d.png" alt="Avatar 2">
                        </div>
                        <div class="avatar-option" onclick="selectAvatar('https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Star-struck/3D/star-struck_3d.png')">
                            <img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Star-struck/3D/star-struck_3d.png" alt="Avatar 3">
                        </div>
                        <div class="avatar-option" onclick="selectAvatar('https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Nerd%20face/3D/nerd_face_3d.png')">
                            <img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Nerd%20face/3D/nerd_face_3d.png" alt="Avatar 4">
                        </div>
                        <div class="avatar-option" onclick="selectAvatar('https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Smiling%20face%20with%20sunglasses/3D/smiling_face_with_sunglasses_3d.png')">
                            <img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Smiling%20face%20with%20sunglasses/3D/smiling_face_with_sunglasses_3d.png" alt="Avatar 5">
                        </div>
                        <div class="avatar-option" onclick="selectAvatar('https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Partying%20face/3D/partying_face_3d.png')">
                            <img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Partying%20face/3D/partying_face_3d.png" alt="Avatar 6">
                        </div>
                    </div>
                </div>
                <div class="form-group">
                    <label for="password">Nueva Contraseña (dejar en blanco para mantener la actual)</label>
                    <input type="password" id="password" name="password">
                </div>
                <button type="submit" class="save-btn">Guardar Cambios</button>
            </form>
        </div>
    </div>

    <script>
        function selectAvatar(url) {
            // Update hidden input value
            document.getElementById('profile_photo').value = url;
            
            // Update visual selection
            const options = document.querySelectorAll('.avatar-option');
            options.forEach(option => {
                if (option.querySelector('img').src === url) {
                    option.classList.add('selected');
                } else {
                    option.classList.remove('selected');
                }
            });

            // Update sidebar profile photo preview
            document.querySelector('.profile-photo').src = url;
        }

        // Set initial selection
        window.onload = function() {
            const currentUrl = document.getElementById('profile_photo').value;
            const options = document.querySelectorAll('.avatar-option');
            options.forEach(option => {
                if (option.querySelector('img').src === currentUrl) {
                    option.classList.add('selected');
                }
            });
        }
    </script>
</body>
</html>
"""

# Template para la página de progreso
PROGRESS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mi Progreso - Sistema de Aprendizaje</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* Reutilizar los estilos base */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Poppins', sans-serif;
        }

        body {
            min-height: 100vh;
            background: #E3F2FD;
            display: flex;
        }

        .sidebar {
            width: 280px;
            background: white;
            padding: 30px;
            display: flex;
            flex-direction: column;
            border-right: 1px solid #e1e1e1;
            position: fixed;
            height: 100vh;
        }

        .profile-section {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            border-bottom: 1px solid #e1e1e1;
        }

        .profile-photo {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            margin-bottom: 15px;
            object-fit: cover;
            border: 3px solid #0091FF;
        }

        .user-name {
            font-size: 1.5em;
            color: #2d3748;
            margin-bottom: 5px;
        }

        .user-email {
            color: #718096;
            font-size: 0.9em;
        }

        .nav-menu {
            list-style: none;
            margin-top: 20px;
        }

        .nav-item {
            margin-bottom: 15px;
        }

        .nav-link {
            display: flex;
            align-items: center;
            padding: 12px 15px;
            color: #2d3748;
            text-decoration: none;
            border-radius: 10px;
            transition: all 0.3s ease;
        }

        .nav-link:hover {
            background: #E3F2FD;
            color: #0091FF;
        }

        .nav-link.active {
            background: #0091FF;
            color: white;
        }

        .main-content {
            flex: 1;
            margin-left: 280px;
            padding: 30px;
        }

        .section-title {
            font-size: 2em;
            color: #2d3748;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 2px solid #0091FF;
        }

        .progress-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
        }

        .progress-card {
            background: white;
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .progress-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }

        .progress-icon {
            font-size: 2em;
            margin-right: 15px;
            color: var(--card-color);
        }

        .progress-title {
            font-size: 1.3em;
            color: #2d3748;
            font-weight: 600;
        }

        .progress-stats {
            display: grid;
            gap: 15px;
        }

        .stat-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            background: #f7fafc;
            border-radius: 10px;
        }

        .stat-label {
            color: #718096;
            font-weight: 500;
        }

        .stat-value {
            color: #2d3748;
            font-weight: 600;
        }

        .progress-bar {
            height: 15px;
            background: #E2E8F0;
            border-radius: 8px;
            overflow: hidden;
            margin: 15px 0;
        }

        .progress-fill {
            height: 100%;
            background: var(--card-color);
            border-radius: 8px;
            transition: width 0.5s ease;
        }

        .progress-text {
            display: flex;
            justify-content: space-between;
            color: #718096;
            font-size: 0.9em;
            font-weight: 500;
        }

        .logout-btn {
            margin-top: auto;
            padding: 12px 20px;
            background: #e53e3e;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            text-align: center;
        }

        .logout-btn:hover {
            background: #c53030;
        }

        @media (max-width: 768px) {
            .sidebar {
                width: 100%;
                height: auto;
                position: relative;
                border-right: none;
                border-bottom: 1px solid #e1e1e1;
            }

            .main-content {
                margin-left: 0;
            }

            .progress-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="profile-section">
            <img src="{{ current_user.profile_photo }}" alt="Profile Photo" class="profile-photo">
            <h2 class="user-name">{{ current_user.name }}</h2>
            <p class="user-email">{{ current_user.email }}</p>
        </div>
        <ul class="nav-menu">
            <li class="nav-item">
                <a href="/dashboard" class="nav-link">
                    📊 Dashboard
                </a>
            </li>
            <li class="nav-item">
                <a href="/profile" class="nav-link active">
                    👤 Mi Perfil
                </a>
            </li>
            <li class="nav-item">
                <a href="/progress" class="nav-link active">
                    📈 Mi Progreso
                </a>
            </li>
        </ul>
        <a href="/logout" class="logout-btn">Cerrar Sesión</a>
    </div>

    <div class="main-content">
        <h1 class="section-title">Mi Progreso</h1>
        <div class="progress-grid">
            {% for field in progress_data %}
            <div class="progress-card" style="--card-color: {{ field.color }}">
                <div class="progress-header">
                    <div class="progress-icon">{{ field.icon }}</div>
                    <h3 class="progress-title">{{ field.name }}</h3>
                </div>
                <div class="progress-stats">
                    <div class="stat-item">
                        <span class="stat-label">Tarjetas Completadas</span>
                        <span class="stat-value">{{ field.completed_cards }}/3</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Mejor Puntuación</span>
                        <span class="stat-value">{{ field.best_score }}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Última Actividad</span>
                        <span class="stat-value">{{ field.last_activity }}</span>
                    </div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ field.progress }}%"></div>
                </div>
                <div class="progress-text">
                    <span>Progreso Total</span>
                    <span class="progress-percentage">{{ "%.0f"|format(field.progress) }}%</span>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

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
    cards = Flashcard.query.filter_by(category=category).all()
    return jsonify([{
        'id': card.id,
        'question': card.question,
        'image_url': card.image_url,
        'options': eval(card.options),
        'correct_option': card.correct_option,
        'feedback': card.feedback
    } for card in cards])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_flashcards()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 