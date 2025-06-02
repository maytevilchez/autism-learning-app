import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Flashcard.css';

const Flashcard = () => {
  const [flashcards, setFlashcards] = useState([]);
  const [currentCard, setCurrentCard] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [score, setScore] = useState(0);

  useEffect(() => {
    const fetchFlashcards = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/flashcards', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        setFlashcards(response.data);
      } catch (error) {
        console.error('Error fetching flashcards:', error);
      }
    };

    fetchFlashcards();
  }, []);

  const handleAnswer = (isCorrect) => {
    if (isCorrect) {
      setScore(score + 1);
    }

    // Guardar el progreso
    axios.post('http://localhost:5000/api/progress', {
      flashcard_id: flashcards[currentCard].id,
      score: isCorrect ? 1 : 0
    }, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    // Pasar a la siguiente tarjeta
    if (currentCard < flashcards.length - 1) {
      setCurrentCard(currentCard + 1);
      setShowAnswer(false);
    }
  };

  if (flashcards.length === 0) {
    return <div>Cargando flashcards...</div>;
  }

  const currentFlashcard = flashcards[currentCard];

  return (
    <div className="flashcard-container">
      <div className="score">Puntuación: {score}</div>
      <div className="flashcard">
        <div className="flashcard-content">
          <img 
            src={currentFlashcard.image_url} 
            alt={currentFlashcard.title}
            className="flashcard-image"
          />
          <h3>{currentFlashcard.title}</h3>
          <p>{currentFlashcard.description}</p>
        </div>
        
        {!showAnswer ? (
          <div className="answer-options">
            <button 
              onClick={() => handleAnswer(true)}
              className="option-button correct"
            >
              Correcto
            </button>
            <button 
              onClick={() => handleAnswer(false)}
              className="option-button incorrect"
            >
              Incorrecto
            </button>
          </div>
        ) : (
          <button 
            onClick={() => setCurrentCard(currentCard + 1)}
            className="next-button"
          >
            Siguiente
          </button>
        )}
      </div>
      <div className="progress">
        Tarjeta {currentCard + 1} de {flashcards.length}
      </div>
    </div>
  );
};

export default Flashcard; 