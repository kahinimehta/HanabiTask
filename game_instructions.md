# How to play

## Set up
1. Generate stimuli using `generate_stimuli.py` into a folder called `Shapes`. The shapes have also been uploaded here in a compressed file called `Shapes.zip` for ease. 
2. Set up and activate a conda environment with PsychoPy. 
3. In Terminal, type : `python task_v0.0py`
4. Follow the instructions to play the game!
   
## Goal
Work with an AI partner (who has seen the same sequence) to recreate a sequence of 3 cards in the correct order.

## The Twist
- You **cannot see your own cards** (they're shown as black boxes to you)
- But you **can see your partner's cards** (the AI's cards)
- Your partner can see your cards but not their own!

## Setup
1. At the start, you'll be shown a **target sequence** of 3 colored shapes
2. You need to memorize this sequence
3. Then you'll work with the AI to recreate it

## On Your Turn, You Can Do 3 Things:

### Press H (Hint)
Tell the AI partner about one of their cards
- Choose which card (1, 2, or 3)
- Tell them either its **COLOR** or its **POSITION** (1 or 2)

### Press P (Play)
Play one of your own cards
- Choose which of your 3 cards to play
- Choose which slot (1, 2, or 3) to put it in

### Press R (Replace)
Swap out one of your cards for a new one
- Use this if you think you have a useless card

## How the AI Helps You
- The AI will give you hints about **your** cards
- When the AI has enough information (both color AND position), it will play its cards automatically
- Work together strategically!

## Winning
- At the end, your played sequence is compared to the target sequence
- You get a score out of 3 (how many cards match in the correct positions)
- You'll play 2 practice trials

## Game Flow
1. **Encoding Phase**: Study the target sequence carefully
2. **Gameplay**: Take turns with the AI giving hints, playing cards, or replacing cards
3. **Completion**: Once all 3 slots are filled, see how well you did!
4. **Results**: Your score and time will be saved automatically to a spreadsheet called `player_accuracy.csv`


Note: The function `run_localizer` is commented out, hence the localizer will not run. You can uncomment this to try out the localizer. 

---


