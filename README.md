# Sistema de Aprendizaje para Niños con Autismo

Esta es una plataforma web diseñada para ayudar en el aprendizaje de niños con autismo, enfocándose en tres áreas principales:
- Desarrollo Emocional
- Conceptos Básicos
- Conocimiento del Entorno

## Características

- Sistema de autenticación de usuarios
- Dashboard interactivo
- Tarjetas de aprendizaje (flashcards)
- Seguimiento de progreso
- Interfaz adaptada para niños
- Diseño responsivo

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio o descargar los archivos

2. Crear un entorno virtual (recomendado):
```bash
python -m venv venv
```

3. Activar el entorno virtual:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

1. Iniciar la aplicación:
```bash
python app.py
```

2. Abrir un navegador web y visitar:
```
http://127.0.0.1:5000
```

3. Registrar una cuenta nueva o iniciar sesión si ya tienes una

## Estructura de la Aplicación

- `app.py`: Archivo principal de la aplicación Flask
- `autism_learning.db`: Base de datos SQLite
- `requirements.txt`: Lista de dependencias
- `templates/`: Directorio con las plantillas HTML (integradas en app.py)

## Desarrollo

La aplicación está construida con:
- Flask (Backend)
- SQLite (Base de datos)
- HTML/CSS/JavaScript (Frontend)
- Poppins Font Family (UI)

## Seguridad

- Contraseñas hasheadas
- Sesiones seguras
- Protección CSRF
- Manejo de errores

## Características de Accesibilidad

- Interfaz simplificada y clara
- Alto contraste para mejor visibilidad
- Animaciones reducidas para evitar distracciones
- Botones grandes y fáciles de clickear
- Instrucciones claras y concisas

## Contribuir

Si deseas contribuir al proyecto:

1. Haz un fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles. 