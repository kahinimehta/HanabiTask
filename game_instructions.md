# How to play

## Set up
1. Generate stimuli using `generate_stimuli.py` into a folder called `Shapes`. The shapes have also been uploaded here in a compressed file called `Shapes.zip` for ease. 
2. Set up and activate a conda environment with PsychoPy. 
3. In Terminal, type : `python task_v0.0py`
4. Follow the instructions to play the game!
   
## Goal
Work with an AI partner (who has seen the same sequence) to recreate a sequence of 3 cards in the correct order.

<img width="300" height="200" alt="Screenshot 2025-10-14 at 12 56 43 AM" src="https://github.com/user-attachments/assets/813b90ee-7c16-48e4-babc-8c695cfbcf0f" />


## The Twist
- You **cannot see your own cards** (they're shown as black boxes to you)
<img width="300" height="200" alt="Screenshot 2025-10-14 at 12 57 16 AM" src="https://github.com/user-attachments/assets/0dae31f8-0b12-4e4f-a74b-ee543618a9ca" />

- But you **can see your partner's cards** (the AI's cards)
<img width="300" height="200" alt="Screenshot 2025-10-14 at 12 58 02 AM" src="https://github.com/user-attachments/assets/77c01ed6-602d-42dc-ace1-ae651264d7bc" />

- Your partner can see your cards but not their own!
<img width="300" height="400" alt="Screenshot 2025-10-14 at 12 58 10 AM" src="https://github.com/user-attachments/assets/50b8875b-8a4d-42de-bbfe-ff12ca819cd7" />

## Setup
1. At the start, you'll be shown a **target sequence** of 3 colored shapes
2. You need to memorize this sequence
3. Then you'll work with the AI to recreate it

## On Your Turn, You Can Do 3 Things:

### Press H (Hint)
Tell the AI partner about one of their cards
- Choose which card (1, 2, or 3)
<img width="300" height="200" alt="Screenshot 2025-10-14 at 1 00 45 AM" src="https://github.com/user-attachments/assets/04c7dee2-8433-4a7f-990c-ac0b5ab31c39" />

- Tell them either its **COLOR** or its **POSITION** (1 or 2)
<img width="300" height="200" alt="Screenshot 2025-10-14 at 1 01 08 AM" src="https://github.com/user-attachments/assets/964c3f9a-6b6d-440d-8921-b680c6afb0dc" />

<img width="300" height="200" alt="Screenshot 2025-10-14 at 12 58 27 AM" src="https://github.com/user-attachments/assets/6201b503-838d-476d-8f52-82c7d03c57ba" />

### Press P (Play)
Play one of your own cards
- Choose which of your 3 cards to play (1, 2, or 3)
  <img width="300" height="200" alt="Screenshot 2025-10-14 at 1 01 53 AM" src="https://github.com/user-attachments/assets/ed132214-a3e5-4ca9-9ac1-2fecb097396b" />

- Choose which slot (1, 2, or 3) to put it in
<img width="300" height="200" alt="Screenshot 2025-10-14 at 1 02 08 AM" src="https://github.com/user-attachments/assets/10c9e699-d0a0-4df2-b99f-b6e4cb59292c" />

<img width="300" height="200" alt="Screenshot 2025-10-14 at 12 58 55 AM" src="https://github.com/user-attachments/assets/48f82db3-cb56-4f15-87b0-0ea6e7da8aca" />

### Press R (Replace)
Swap out one of your cards for a new one
- Use this if you think you have a useless card

## How the AI Helps You
- The AI will give you hints about **your** cards

<img width="300" height="200" alt="Screenshot 2025-10-14 at 12 59 28 AM" src="https://github.com/user-attachments/assets/ba0f3b5b-b1a0-4293-bc53-7b375b0c5875" />

- When the AI has enough information (both color AND position), it will play its cards automatically
<img width="300" height="200" alt="Screenshot 2025-10-14 at 12 59 49 AM" src="https://github.com/user-attachments/assets/8e7deb46-337a-4046-8e4d-76fecf3c1f84" />
- Work together strategically!

## Winning
- At the end, your played sequence is compared to the target sequence
- You get a score out of 3 (how many cards match in the correct positions)
- You'll play 2 practice trials
<img width="300" height="200" alt="Screenshot 2025-10-14 at 1 00 09 AM" src="https://github.com/user-attachments/assets/caf39ce1-cb1f-47c8-a2b8-38544de48112" />

## Game Flow
1. **Encoding Phase**: Study the target sequence carefully
2. **Gameplay**: Take turns with the AI giving hints, playing cards, or replacing cards
3. **Completion**: Once all 3 slots are filled, see how well you did!
4. **Results**: Your score and time will be saved automatically to a spreadsheet called `player_accuracy.csv`


Note: The function `run_localizer` is commented out, hence the localizer will not run. You can uncomment this to try out the localizer. 

---


