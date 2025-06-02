from app import db, app
from app import User, Flashcard, UserProgress
from werkzeug.security import generate_password_hash
import os

def init_database():
    with app.app_context():
        # Verificar si el archivo de base de datos existe
        db_path = os.path.join(os.path.dirname(__file__), 'autism_learning.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            print("Base de datos anterior eliminada.")
        
        print("Creando nueva base de datos...")
        
        # Crear todas las tablas
        db.create_all()
        print("Tablas creadas correctamente.")
        
        # Crear usuario de prueba
        test_user = User(
            name='Test User',
            email='test@example.com',
            password_hash=generate_password_hash('password123', method='sha256')
        )
        
        try:
            db.session.add(test_user)
            db.session.commit()
            print("Usuario de prueba creado correctamente.")
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear usuario de prueba (puede que ya exista): {e}")

        # Crear flashcards de ejemplo
        flashcards = [
            # Desarrollo Emocional
            Flashcard(
                category='emociones',
                question='¿Cómo te sientes cuando ves esta cara?',
                image_url='https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Grinning%20face/3D/grinning_face_3d.png',
                options=str(['Feliz', 'Triste', 'Enojado', 'Asustado']),
                correct_option=0,
                feedback='¡Muy bien! Cuando alguien sonríe así, está feliz y contento.'
            ),
            Flashcard(
                category='emociones',
                question='¿Qué emoción muestra esta cara?',
                image_url='https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Crying%20face/3D/crying_face_3d.png',
                options=str(['Triste', 'Feliz', 'Sorprendido', 'Enojado']),
                correct_option=0,
                feedback='¡Correcto! Es importante reconocer cuando alguien está triste para poder ayudar.'
            ),
            # Conceptos Básicos
            Flashcard(
                category='conceptos',
                question='¿Cuántos dedos hay en la imagen?',
                image_url='https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Hand%20with%20fingers%20splayed/3D/hand_with_fingers_splayed_3d.png',
                options=str(['5', '3', '4', '6']),
                correct_option=0,
                feedback='¡Correcto! En una mano tenemos 5 dedos.'
            ),
            Flashcard(
                category='conceptos',
                question='¿Qué número es este?',
                image_url='https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Keycap%20digit%20three/3D/keycap_digit_three_3d.png',
                options=str(['3', '8', '5', '2']),
                correct_option=0,
                feedback='¡Excelente! Este es el número 3.'
            ),
            Flashcard(
                category='conceptos',
                question='¿Cuál es más grande?',
                image_url='https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Elephant/3D/elephant_3d.png',
                options=str(['Elefante', 'Ratón', 'Gato', 'Conejo']),
                correct_option=0,
                feedback='¡Muy bien! El elefante es el animal más grande de estos.'
            ),
            # Conocimiento del Entorno
            Flashcard(
                category='entorno',
                question='¿Qué animal es este?',
                image_url='https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Dog%20face/3D/dog_face_3d.png',
                options=str(['Perro', 'Gato', 'Conejo', 'Pájaro']),
                correct_option=0,
                feedback='¡Correcto! Es un perro, un animal doméstico muy común.'
            ),
            Flashcard(
                category='entorno',
                question='¿Qué clima representa esta imagen?',
                image_url='https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Sun/3D/sun_3d.png',
                options=str(['Soleado', 'Lluvioso', 'Nublado', 'Nevado']),
                correct_option=0,
                feedback='¡Muy bien! Es un día soleado.'
            )
        ]
        
        print(f"\nAgregando {len(flashcards)} flashcards...")
        # Agregar las flashcards a la base de datos
        for flashcard in flashcards:
            db.session.add(flashcard)
        
        # Guardar los cambios
        try:
            db.session.commit()
            print("\n¡Base de datos inicializada correctamente!")
            print(f"Se agregaron {len(flashcards)} flashcards de ejemplo")
            
            # Verificar que las flashcards se guardaron
            saved_cards = Flashcard.query.all()
            print(f"\nFlashcards en la base de datos: {len(saved_cards)}")
            print("\nCategorías disponibles:")
            categories = set(card.category for card in flashcards)
            for category in categories:
                count = sum(1 for card in flashcards if card.category == category)
                print(f"- {category}: {count} flashcards")
        except Exception as e:
            print("\nError al inicializar la base de datos:", str(e))
            db.session.rollback()

if __name__ == '__main__':
    init_database() 