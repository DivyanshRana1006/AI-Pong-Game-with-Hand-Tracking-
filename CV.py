import cv2
import mediapipe as mp
import numpy as np
import random

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# Game variables
width, height = 640, 480
paddle_width, paddle_height = 100, 10
ball_radius = 10
ball_speed_x, ball_speed_y = 5, 5
player_x, player_y = (width // 2, height - 30)
ai_x, ai_y = (width // 2, 30)
ball_x, ball_y = (width // 2, height // 2)
score_player, score_ai = 0, 0

# Capture Video
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the frame and detect hands
    results = hands.process(rgb_frame)

    # Move player paddle with hand
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            index_x = int(hand_landmarks.landmark[8].x * width)  # Index finger x position
            player_x = np.clip(index_x, paddle_width // 2, width - paddle_width // 2)

    # Move AI paddle (follows the ball)
    ai_x = np.clip(ball_x, paddle_width // 2, width - paddle_width // 2)

    # Update ball position
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # Ball collisions with walls
    if ball_x - ball_radius < 0 or ball_x + ball_radius > width:
        ball_speed_x *= -1

    # Ball collision with paddles
    if (player_y - ball_radius < ball_y < player_y + paddle_height and abs(player_x - ball_x) < paddle_width // 2) or \
       (ai_y + paddle_height > ball_y > ai_y - ball_radius and abs(ai_x - ball_x) < paddle_width // 2):
        ball_speed_y *= -1

    # Scoring system
    if ball_y < 0:
        score_player += 1
        ball_x, ball_y = width // 2, height // 2
        ball_speed_y *= random.choice([-1, 1])

    if ball_y > height:
        score_ai += 1
        ball_x, ball_y = width // 2, height // 2
        ball_speed_y *= random.choice([-1, 1])

    # Draw paddles and ball
    cv2.rectangle(frame, (player_x - paddle_width // 2, player_y), 
                  (player_x + paddle_width // 2, player_y + paddle_height), (0, 255, 0), -1)
    cv2.rectangle(frame, (ai_x - paddle_width // 2, ai_y), 
                  (ai_x + paddle_width // 2, ai_y + paddle_height), (255, 0, 0), -1)
    cv2.circle(frame, (ball_x, ball_y), ball_radius, (0, 0, 255), -1)

    # Display scores
    cv2.putText(frame, f"Player: {score_player}", (20, height - 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(frame, f"AI: {score_ai}", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Show frame
    cv2.imshow("AI Pong with Hand Control", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
