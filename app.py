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

# Template HTML para la página de inicio
HTML_TEMPLATE = '''
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
            <button onclick="toggleForms()" style="background: white; color: #0091FF;">Registrarse</button>
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
                    <button onclick="toggleForms()" style="background: white; color: #0091FF;">Iniciar Sesión</button>
                `;
            } else {
                loginForm.style.display = 'block';
                registerForm.style.display = 'none';
                authInfo.innerHTML = `
                    <h2>¿Aún no tienes una cuenta?</h2>
                    <p>Regístrate para que puedas iniciar sesión</p>
                    <button onclick="toggleForms()" style="background: white; color: #0091FF;">Registrarse</button>
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
'''

# Template para el Dashboard
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - Sistema de Aprendizaje</title>
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
            padding: 20px;
        }

        .navbar {
            background: white;
            padding: 15px 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }

        .nav-links {
            display: flex;
            gap: 20px;
        }

        .nav-link {
            color: #333;
            text-decoration: none;
            padding: 8px 15px;
            border-radius: 8px;
            transition: all 0.3s ease;
        }

        .nav-link:hover {
            background: #0091FF;
            color: white;
        }

        .user-info {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .user-photo {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            object-fit: cover;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            padding: 20px;
        }

        .card {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
        }

        .card-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
        }

        .card-icon {
            font-size: 2em;
        }

        .card-title {
            font-size: 1.5em;
            font-weight: 600;
            color: #333;
        }

        .card-description {
            color: #666;
            margin-bottom: 20px;
            line-height: 1.6;
        }

        .progress-bar {
            width: 100%;
            height: 10px;
            background: #e1e1e1;
            border-radius: 5px;
            overflow: hidden;
            margin-bottom: 10px;
        }

        .progress-fill {
            height: 100%;
            background: #0091FF;
            border-radius: 5px;
            transition: width 0.3s ease;
        }

        .progress-text {
            display: flex;
            justify-content: space-between;
            color: #666;
            font-size: 0.9em;
        }

        .start-button {
            display: inline-block;
            padding: 12px 25px;
            background: #0091FF;
            color: white;
            border-radius: 10px;
            text-decoration: none;
            margin-top: 20px;
            transition: all 0.3s ease;
        }

        .start-button:hover {
            background: #007acc;
            transform: translateY(-2px);
        }

        .completed {
            background: #4CAF50;
        }

        @media (max-width: 768px) {
            .navbar {
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }

            .nav-links {
                flex-direction: column;
            }

            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-links">
            <a href="/dashboard" class="nav-link">Inicio</a>
            <a href="/progress" class="nav-link">Progreso</a>
            <a href="/profile" class="nav-link">Perfil</a>
            <a href="/logout" class="nav-link">Cerrar Sesión</a>
        </div>
        <div class="user-info">
            <img src="{{ current_user.profile_photo }}" alt="Foto de perfil" class="user-photo">
            <span>{{ current_user.name }}</span>
        </div>
    </nav>

    <div class="container">
        <div class="grid">
            {% for field in study_fields %}
            <div class="card" style="border-top: 5px solid {{ field.color }}">
                <div class="card-header">
                    <span class="card-icon">{{ field.icon }}</span>
                    <h2 class="card-title">{{ field.name }}</h2>
                </div>
                <p class="card-description">{{ field.description }}</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ field.progress }}%; background: {{ field.color }}"></div>
                </div>
                <div class="progress-text">
                    <span>{{ field.completed_cards }}/{{ field.total_cards }} tarjetas</span>
                    <span>{{ field.progress }}%</span>
                </div>
                <a href="/{{ field.route }}" class="start-button" style="background: {{ field.color }}">
                    {% if field.completed %}
                        Repasar
                    {% else %}
                        Comenzar
                    {% endif %}
                </a>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''

# Template para el Perfil
PROFILE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Perfil - Sistema de Aprendizaje</title>
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
            padding: 20px;
        }

        .navbar {
            background: white;
            padding: 15px 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }

        .nav-links {
            display: flex;
            gap: 20px;
        }

        .nav-link {
            color: #333;
            text-decoration: none;
            padding: 8px 15px;
            border-radius: 8px;
            transition: all 0.3s ease;
        }

        .nav-link:hover {
            background: #0091FF;
            color: white;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }

        .profile-header {
            display: flex;
            align-items: center;
            gap: 30px;
            margin-bottom: 40px;
        }

        .profile-photo {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            object-fit: cover;
            border: 5px solid #0091FF;
        }

        .profile-info h1 {
            font-size: 2em;
            color: #333;
            margin-bottom: 10px;
        }

        .profile-info p {
            color: #666;
            font-size: 1.1em;
        }

        .form-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }

        input {
            width: 100%;
            padding: 12px;
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
            padding: 12px 25px;
            background: #0091FF;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        button:hover {
            background: #007acc;
            transform: translateY(-2px);
        }

        @media (max-width: 768px) {
            .navbar {
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }

            .nav-links {
                flex-direction: column;
            }

            .profile-header {
                flex-direction: column;
                text-align: center;
            }

            .container {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-links">
            <a href="/dashboard" class="nav-link">Inicio</a>
            <a href="/progress" class="nav-link">Progreso</a>
            <a href="/profile" class="nav-link">Perfil</a>
            <a href="/logout" class="nav-link">Cerrar Sesión</a>
        </div>
    </nav>

    <div class="container">
        <div class="profile-header">
            <img src="{{ current_user.profile_photo }}" alt="Foto de perfil" class="profile-photo">
            <div class="profile-info">
                <h1>{{ current_user.name }}</h1>
                <p>{{ current_user.email }}</p>
            </div>
        </div>

        <form action="/update-profile" method="POST">
            <div class="form-group">
                <label for="name">Nombre</label>
                <input type="text" id="name" name="name" value="{{ current_user.name }}" required>
            </div>

            <div class="form-group">
                <label for="email">Correo Electrónico</label>
                <input type="email" id="email" name="email" value="{{ current_user.email }}" required>
            </div>

            <div class="form-group">
                <label for="profile_photo">URL de Foto de Perfil</label>
                <input type="url" id="profile_photo" name="profile_photo" value="{{ current_user.profile_photo }}">
            </div>

            <div class="form-group">
                <label for="password">Nueva Contraseña (dejar en blanco para mantener la actual)</label>
                <input type="password" id="password" name="password">
            </div>

            <button type="submit">Actualizar Perfil</button>
        </form>
    </div>
</body>
</html>
'''

# Template para la página de Progreso
PROGRESS_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Progreso - Sistema de Aprendizaje</title>
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
            padding: 20px;
        }

        .navbar {
            background: white;
            padding: 15px 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }

        .nav-links {
            display: flex;
            gap: 20px;
        }

        .nav-link {
            color: #333;
            text-decoration: none;
            padding: 8px 15px;
            border-radius: 8px;
            transition: all 0.3s ease;
        }

        .nav-link:hover {
            background: #0091FF;
            color: white;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .progress-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            padding: 20px;
        }

        .progress-card {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }

        .progress-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
        }

        .progress-icon {
            font-size: 2em;
        }

        .progress-title {
            font-size: 1.5em;
            font-weight: 600;
            color: #333;
        }

        .progress-bar {
            width: 100%;
            height: 10px;
            background: #e1e1e1;
            border-radius: 5px;
            overflow: hidden;
            margin: 20px 0;
        }

        .progress-fill {
            height: 100%;
            background: #0091FF;
            border-radius: 5px;
            transition: width 0.3s ease;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-top: 20px;
        }

        .stat-item {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }

        .stat-value {
            font-size: 1.5em;
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }

        .stat-label {
            color: #666;
            font-size: 0.9em;
        }

        @media (max-width: 768px) {
            .navbar {
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }

            .nav-links {
                flex-direction: column;
            }

            .progress-grid {
                grid-template-columns: 1fr;
            }

            .stats {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-links">
            <a href="/dashboard" class="nav-link">Inicio</a>
            <a href="/progress" class="nav-link">Progreso</a>
            <a href="/profile" class="nav-link">Perfil</a>
            <a href="/logout" class="nav-link">Cerrar Sesión</a>
        </div>
    </nav>

    <div class="container">
        <div class="progress-grid">
            {% for item in progress_data %}
            <div class="progress-card">
                <div class="progress-header">
                    <span class="progress-icon">{{ item.icon }}</span>
                    <h2 class="progress-title">{{ item.name }}</h2>
                </div>

                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ item.progress }}%; background: {{ item.color }}"></div>
                </div>

                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-value">{{ item.completed_cards }}/{{ item.total_cards }}</div>
                        <div class="stat-label">Tarjetas Completadas</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{{ item.best_score }}</div>
                        <div class="stat-label">Mejor Puntuación</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{{ item.progress }}%</div>
                        <div class="stat-label">Progreso Total</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{{ item.last_activity }}</div>
                        <div class="stat-label">Última Actividad</div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''

# Template para las flashcards
FLASHCARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Aprendizaje - Sistema de Aprendizaje</title>
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
            padding: 20px;
        }

        .navbar {
            background: white;
            padding: 15px 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }

        .nav-links {
            display: flex;
            gap: 20px;
        }

        .nav-link {
            color: #333;
            text-decoration: none;
            padding: 8px 15px;
            border-radius: 8px;
            transition: all 0.3s ease;
        }

        .nav-link:hover {
            background: #0091FF;
            color: white;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
        }

        .flashcard {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
            text-align: center;
        }

        .flashcard img {
            max-width: 300px;
            height: auto;
            margin: 20px 0;
            border-radius: 10px;
        }

        .question {
            font-size: 1.5em;
            color: #333;
            margin-bottom: 30px;
        }

        .options {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }

        .option {
            padding: 15px;
            border: 2px solid #e1e1e1;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .option:hover {
            border-color: #0091FF;
            background: #f5f5f5;
        }

        .option.selected {
            background: #0091FF;
            color: white;
            border-color: #0091FF;
        }

        .option.correct {
            background: #4CAF50;
            color: white;
            border-color: #4CAF50;
        }

        .option.incorrect {
            background: #f44336;
            color: white;
            border-color: #f44336;
        }

        .feedback {
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            display: none;
        }

        .feedback.correct {
            background: #E8F5E9;
            color: #2E7D32;
            border: 1px solid #A5D6A7;
        }

        .feedback.incorrect {
            background: #FFEBEE;
            color: #C62828;
            border: 1px solid #FFCDD2;
        }

        .progress-bar {
            width: 100%;
            height: 10px;
            background: #e1e1e1;
            border-radius: 5px;
            overflow: hidden;
            margin-bottom: 20px;
        }

        .progress-fill {
            height: 100%;
            background: #0091FF;
            border-radius: 5px;
            transition: width 0.3s ease;
        }

        .next-button {
            padding: 12px 25px;
            background: #0091FF;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
            display: none;
        }

        .next-button:hover {
            background: #007acc;
            transform: translateY(-2px);
        }

        @media (max-width: 768px) {
            .navbar {
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }

            .nav-links {
                flex-direction: column;
            }

            .options {
                grid-template-columns: 1fr;
            }

            .flashcard {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-links">
            <a href="/dashboard" class="nav-link">Inicio</a>
            <a href="/progress" class="nav-link">Progreso</a>
            <a href="/profile" class="nav-link">Perfil</a>
            <a href="/logout" class="nav-link">Cerrar Sesión</a>
        </div>
    </nav>

    <div class="container">
        <div class="progress-bar">
            <div class="progress-fill" id="progressBar" style="width: 0%"></div>
        </div>

        <div class="flashcard" id="flashcard">
            <div class="question" id="question"></div>
            <img id="questionImage" src="" alt="Imagen de la pregunta">
            <div class="options" id="options"></div>
            <div class="feedback" id="feedback"></div>
            <button class="next-button" id="nextButton">Siguiente</button>
        </div>
    </div>

    <script>
        let currentCardIndex = 0;
        let cards = [];
        let score = 0;
        let selectedOption = null;
        let category = window.location.pathname.split('/')[1];

        // Elementos del DOM
        const questionEl = document.getElementById('question');
        const questionImageEl = document.getElementById('questionImage');
        const optionsEl = document.getElementById('options');
        const feedbackEl = document.getElementById('feedback');
        const nextButton = document.getElementById('nextButton');
        const progressBar = document.getElementById('progressBar');

        // Cargar las flashcards
        async function loadFlashcards() {
            try {
                const response = await fetch(`/api/flashcards/${category}`);
                cards = await response.json();
                showCard(currentCardIndex);
            } catch (error) {
                console.error('Error cargando flashcards:', error);
            }
        }

        // Mostrar una tarjeta
        function showCard(index) {
            if (index >= cards.length) {
                saveProgress();
                return;
            }

            const card = cards[index];
            questionEl.textContent = card.question;
            questionImageEl.src = card.image_url;
            
            optionsEl.innerHTML = '';
            card.options.forEach((option, i) => {
                const button = document.createElement('button');
                button.className = 'option';
                button.textContent = option;
                button.onclick = () => selectOption(i);
                optionsEl.appendChild(button);
            });

            feedbackEl.style.display = 'none';
            nextButton.style.display = 'none';
            selectedOption = null;

            updateProgressBar();
        }

        // Seleccionar una opción
        function selectOption(index) {
            if (selectedOption !== null) return;

            selectedOption = index;
            const card = cards[currentCardIndex];
            const options = document.querySelectorAll('.option');

            options[index].classList.add('selected');

            if (index === card.correct_option) {
                score++;
                options[index].classList.add('correct');
                feedbackEl.className = 'feedback correct';
                feedbackEl.textContent = card.feedback;
            } else {
                options[index].classList.add('incorrect');
                options[card.correct_option].classList.add('correct');
                feedbackEl.className = 'feedback incorrect';
                feedbackEl.textContent = 'Intenta de nuevo. ' + card.feedback;
            }

            feedbackEl.style.display = 'block';
            nextButton.style.display = 'block';
        }

        // Actualizar la barra de progreso
        function updateProgressBar() {
            const progress = ((currentCardIndex + 1) / cards.length) * 100;
            progressBar.style.width = `${progress}%`;
        }

        // Guardar el progreso
        async function saveProgress() {
            const percentage = (score / cards.length) * 100;
            const completed = currentCardIndex >= cards.length - 1;

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

                if (response.ok) {
                    window.location.href = '/dashboard';
                }
            } catch (error) {
                console.error('Error guardando progreso:', error);
            }
        }

        // Evento para el botón siguiente
        nextButton.onclick = () => {
            currentCardIndex++;
            showCard(currentCardIndex);
        };

        // Cargar las flashcards al iniciar
        loadFlashcards();
    </script>
</body>
</html>
'''

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

# Rutas para las categorías de aprendizaje
@app.route('/emociones')
@app.route('/conceptos')
@app.route('/entorno')
@login_required
def learning_category():
    return render_template_string(FLASHCARD_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True) 