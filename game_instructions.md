# How to Play the Memory Card Game

## Set up
1. Generate stimuli using `generate_stimuli.py` into a folder called `Shapes`. The shapes have also been uploaded here in a compressed file called `Shapes.zip` for ease. 
2. Set up and activate a conda environment with PsychoPy. 
3. In Terminal, type : `python task_v0.1.py`
4. Follow the instructions to play the game!
   
## Goal
Work with an AI partner (who has seen the same sequence) to recreate a sequence of 3 cards in the correct order.

## The Twist
- You **cannot see your own cards** (they're shown as black boxes to you)
- But you **can see your partner's cards** (the AI's cards)
- Your partner can see your cards but not their own!

## Setup
1. At the start, you'll be shown a **target sequence** of 3 colored shapes (cards appear one by one: first card, then first+second, then all three)
2. You need to memorize this sequence
3. Then you'll work with the AI to recreate it

## On Your Turn, You Can Do 3 Things:

### Click HINT
Tell the AI partner about one of their cards
- Click the **HINT** button
- Click on one of the AI's cards (top row) to hint about
- Click **COLOR** or **POSITION** to specify what type of hint to give
- The AI will receive your hint and may play a card if it has enough information

### Click PLAY
Play one of your own cards
- Click the **PLAY** button
- Click on one of YOUR cards (bottom row) to play
- Click on a SLOT (middle row) to place the card
- ⚠️ Remember: you can't see your own cards!

### Click REPLACE
Swap out one of your cards for a new one
- Click the **REPLACE** button
- Click on one of YOUR cards (bottom row) to replace
- Use this if you think you have a useless card

## Visual Hint System
Your cards (bottom row) will show hints as you receive them:
- **Colored squares**: When AI tells you the color of a card
- **White arrows with black outline**: When AI tells you the position of a card
  - `^` = up
  - `v` = down  
  - `<` = left
  - `>` = right

## How the AI Helps You
- The AI will give you hints about **your** cards
- When the AI has enough information (both color AND position), it will play its cards automatically
- Work together strategically!

## Winning
- At the end, your played sequence is compared to the target sequence
- You get a score out of 3 (how many cards match in the correct positions)
- You'll play 2 practice trials

## Game Flow
1. **Encoding Phase**: Study the target sequence carefully (cards appear sequentially)
2. **Gameplay**: Take turns with the AI giving hints, playing cards, or replacing cards
3. **Completion**: Once all 3 slots are filled, see how well you did!
4. **Results**: Your score, time, and turn-by-turn actions will be saved automatically to spreadsheets:
   - `player_accuracy.csv` - Overall trial results
   - `turn_by_turn_log.csv` - Detailed action log with reaction times

## Interface Notes
- **Mouse/Touch Interface**: Click on cards and buttons to interact
- **Persistent Display**: All cards stay visible throughout the game
- **Visual Feedback**: Selected cards are highlighted with red borders
- **Touch Screen Compatible**: Works well on touch screens

Note: The function `run_localizer` is commented out, hence the localizer will not run. You can uncomment this to try out the localizer.

---
