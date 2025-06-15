# Language Learning Quiz Application

This application provides an interactive language learning experience with quizzes in multiple languages and difficulty levels.

## Features

- Multiple languages supported
- Three difficulty levels: Beginner, Intermediate, and Advanced
- Various question types for effective language learning
- Progress tracking and achievements
- User profiles and statistics

## Setup Instructions

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python app.py
   ```

3. Access the application in your browser at `http://localhost:5000`

## Using the Quiz Feature

1. Log in to the application
2. Navigate to the Quiz section
3. Select your preferred language
4. Choose a difficulty level
5. Complete the quiz to earn points and track your progress

## Question Types

The application includes various types of questions:

- Multiple choice questions
- Fill-in-the-blank exercises
- Matching exercises
- Sentence construction
- Grammar application

## Technical Details

The application uses a SQLite database to store:
- User information and progress
- Quiz results and statistics
- Achievements and badges

All questions are pre-defined in the quiz_data.py file, organized by language and difficulty level.
