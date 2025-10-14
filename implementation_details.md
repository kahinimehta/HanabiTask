# Implementation Guide: Memory Card Game (task_v0.0.py)

Tool used: Cursor 

## Table of Contents
1. [Overview](#overview)
2. [Setup and Configuration](#setup-and-configuration)
3. [Core Utility Functions](#core-utility-functions)
4. [Localizer Task](#localizer-task)
5. [Practice Game](#practice-game)
6. [AI Implementation](#ai-implementation)
7. [Game Flow](#game-flow)
8. [Data Structures](#data-structures)

---

## Overview

This implementation consists of three main components:
1. **Localizer Task**: A 1-back memory task for color and position
2. **Practice Game**: A cooperative card game inspired by Hanabi
3. **Optimal AI**: An intelligent agent that plays cooperatively with the participant

### Technologies Used
- **PsychoPy**: For visual presentation and event handling
- **PIL (Pillow)**: For image processing
- **NumPy**: For data analysis
- **Python Standard Library**: For file operations and randomization

---

## Setup and Configuration

### Window Initialization
```python
win = visual.Window(size=[1280, 720], color='white', units='height', fullscr=False)
```
- Creates a 1280x720 window with white background
- Uses height-based units for cross-platform consistency
- Not fullscreen for development (change `fullscr=True` for experiments)

### Stimulus Loading
```python
stimuli = [os.path.join(save_dir, f) for f in os.listdir(save_dir)
           if f.endswith(".png") and "_rotated" not in f]
```
- Loads all non-rotated PNG files from the `Shapes` directory
- Expected naming convention: `{color}_{position}_square.png`
- Example: `yellow_up_square.png`, `blue_left_square.png`

### Safe Image Loader Function
```python
def load_shape_image(win, img_path):
```
**Purpose**: Handles macOS NSCFString issue when loading images

**Implementation**:
1. Opens image with PIL
2. Converts to RGB format
3. Saves to temporary file
4. Loads into PsychoPy ImageStim
5. Returns the stimulus object

**Why needed**: Direct image loading can cause crashes on macOS due to string encoding issues

---

## Core Utility Functions

### 1. `show_instructions(text)`
**Purpose**: Display text and wait for spacebar

**Parameters**:
- `text`: String to display

**Behavior**:
1. Appends "Press SPACE to continue" to text
2. Displays on screen
3. Clears event buffer
4. Waits for spacebar press

### 2. `jitter(min_t=0.5, max_t=1.5)`
**Purpose**: Generate random time intervals for inter-trial timing

**Returns**: Random float between min_t and max_t seconds

### 3. `safe_wait(secs)`
**Purpose**: Non-blocking wait that prevents window event dispatch issues

**Implementation**: Uses core.Clock() instead of core.wait() to avoid triggering window events during timing-critical periods

---

## Localizer Task

### Overview
The localizer consists of two sequential 1-back tasks:
1. **Color 1-back** (120 trials): Respond when color repeats
2. **Position 1-back** (120 trials): Respond when position repeats

### Function: `run_localizer()`

#### Setup Phase
```python
colors = ["yellow", "blue", "cyan", "orange"]
positions = ["up", "down", "left", "right"]
base_reps = 15  # each unique color-position image appears 15× → 240 total
```

**Stimulus Pool Construction**:
- 16 unique stimuli (4 colors × 4 positions)
- Each repeated 15 times = 240 total trials
- Pool is shuffled randomly
- 120 trials for color block, 120 for position block

#### Smart Stochastic Sequence Generation

**Color Block Sequence**:
```python
if i > 0 and random.random() < 0.35 and color_seq[-1] in avail:
    color_seq.append(color_seq[-1])  # 35% chance of repeat
else:
    choices = [c for c in colors if c in avail and (not color_seq or c != color_seq[-1])]
    color_seq.append(random.choice(choices))  # Different color
```

**Logic**:
- 35% probability of creating a match (same color as previous)
- Otherwise, select a different color from available pool
- Ensures balanced distribution of match/non-match trials

#### Trial Execution

**Each Trial**:
1. **Fixation**: Display "+" for 0.5-1.5 seconds (jittered)
2. **Stimulus**: Display shape at position-appropriate location with offset
3. **Response Window**: 1.0 second maximum wait for spacebar
4. **Feedback**: 0.6 seconds
   - "Correct!" = Hit (match + press)
   - "Miss!" = Miss (match + no press)
   - "False alarm!" = False alarm (no match + press)
   - "" (blank) = Correct rejection (no match + no press)

#### Position Offsets
```python
stim.pos = {
    "up": (0, offset),      # offset = 0.3
    "down": (0, -offset),
    "left": (-offset, 0),
    "right": (offset, 0),
}[pos]
```
Shapes are displaced from center to match their semantic position (on top of already being offset when stimuli are created)

#### Data Collection

**Results Dictionary**:
```python
{
    "block": "color" or "position",
    "stim": stim_path,
    "color": color_now,
    "position": pos,
    "match": is_match,
    "pressed": pressed,
    "rt": rt,  # Reaction time in seconds (None if no response)
    "correct": correct
}
```

#### Summary Statistics
- Overall accuracy
- Color block accuracy
- Position block accuracy
- Actual runtime
- Stimulus appearance counts (should be balanced)
- Fallback count (if pool exhaustion required fallback draws)

---

## Practice Game

### Overview
Cooperative memory game where:
- Participant and AI have 3 cards each
- Neither player can see their own cards
- Goal: Recreate a 3-card target sequence
- Players give hints, play cards, or replace cards

### Function: `run_practice()`

---

## Helper Functions (Practice Game)

### 1. `parse_stim_filename(path)`
**Purpose**: Extract color and position from filename

**Example**: 
- Input: `"yellow_up_square.png"`
- Output: `("yellow", "up")`

### 2. `find_stim_file(color, pos)`
**Purpose**: Find file path for given color-position combination

**Implementation**: Searches stimuli list for matching filename

### 3. `draw_box(center, w=0.20, h=0.20, line="black", fill=None)`
**Purpose**: Draw rectangular card placeholder

**Parameters**:
- `center`: (x, y) position
- `w`, `h`: Width and height
- `line`: Border color
- `fill`: Fill color (None = transparent)

### 4. `draw_card(center, color, pos, faceup=True, thumb=False)`
**Purpose**: Draw a card with its image

**Parameters**:
- `faceup`: If False, draws black box (hidden card)
- `thumb`: If True, uses smaller size (0.10 vs 0.15)

### 5. `render_board_with_participant_cards(...)`
**Purpose**: Main rendering function for game board

**Layout**:
```
Top (y=0.40):    [AI Card 1] [AI Card 2] [AI Card 3]
Middle (y=0.10): [Slot 1]    [Slot 2]    [Slot 3]
Bottom (y=-0.20):[Your Card 1][Your Card 2][Your Card 3]
```

**Parameters**:
- `computer_cards`: AI's cards (visible to participant)
- `participant_cards`: Participant's cards
- `played_sequence`: Cards already played
- `hint_text`: Text displayed at bottom
- `show_participant_cards`: If True, reveals participant's cards (for selection)
- `selected_card`: Highlights selected card with red border

### 6. `choose_index(prompt, options=3)`
**Purpose**: Get player selection (1-3)

**Returns**: Index (0-2)

**Key Mapping**: Keys '1', '2', '3' map to indices 0, 1, 2

### 7. `get_available_cards_for_replacement(all_cards_in_use, missing_sequence_cards)`
**Purpose**: Find cards not currently in play

**Logic**:
1. Get all possible cards from stimuli
2. Remove cards currently in use
3. Prioritize missing sequence cards if any
4. Return random available card

**Critical Feature**: Ensures missing sequence cards are drawn when available

### 8. `draw_new_card(all_cards_in_use, missing_sequence_cards=[])`
**Purpose**: Wrapper for getting replacement card

### 9. `check_missing_sequence_cards(true_sequence, computer_cards, participant_cards, played_sequence)`
**Purpose**: Identify sequence cards not in circulation

**Returns**: List of missing cards

**Use Case**: Prevents game from becoming impossible if sequence card is replaced

### 10. `show_instructions_with_space(text, wait_time=0.1)`
**Purpose**: Improved instruction display with better space key handling

**Improvements over basic version**:
- Clears event buffer
- Small wait to prevent double-registration
- Uses polling loop instead of blocking wait
- More reliable across platforms

### 11. `get_player_name()`
**Purpose**: Text input for player name

**Features**:
- Real-time text display
- Backspace support
- Enter to confirm
- Escape to quit
- Accepts alphanumeric + space, underscore, hyphen

### 12. `save_results_to_spreadsheet(player_name, trial_results)`
**Purpose**: Save trial results to CSV

**File Format** (`player_accuracy.csv`):
```
Player_Name,Trial,Score,Time_Seconds,Time_Formatted,Timestamp
John,1,2,145.32,2:25,2025-10-14 15:30:45
John,2,3,132.18,2:12,2025-10-14 15:30:45
```

**Behavior**:
- Creates file if doesn't exist
- Appends to existing file
- Writes header only once
- Timestamps with date and time

---

## AI Implementation

### Class: `OptimalAI`

The AI is designed to play **optimally** while being **realistic** (not omniscient).

#### Initialization
```python
def __init__(self, true_sequence, participant_cards):
```

**AI Knowledge**:
- Knows true sequence (game objective)
- Can see participant's cards
- Cannot see its own cards
-  Must rely on hints to learn about own cards

**Data Structures**:

1. **`self.true_sequence`**: The target sequence (3 cards)

2. **`self.participant_cards`**: Current participant cards (updated dynamically)

3. **`self.ai_cards`**: Initialized as `[None, None, None]` (AI doesn't know own cards)

4. **`self.hint_history`**: Record of all hints given/received
   ```python
   {
       'type': 'received' or 'given',
       'hint_type': 'color' or 'position',
       'hint_value': actual value,
       'target_card': index,
       'turn': turn number
   }
   ```

5. **`self.sequence_knowledge`**: AI's belief about what's been played
   - `[None, None, None]` initially
   - Updates when cards are played
   - Used to avoid replaying same slot

6. **`self.ai_card_inferences`**: What AI knows about its own cards from hints
   ```python
   {
       card_index: {
           'color': 'yellow' or None,
           'position': 'up' or None,
           'actual_card': (color, pos)
       }
   }
   ```

7. **`self.participant_playable_cards`**: List of participant cards that are in sequence
   ```python
   [(card_index, card, slot_index), ...]
   ```

8. **`self.urgency_scores`**: Priority score for each sequence slot `[0-8]`

9. **Progress Tracking**:
   - `self.stall_count`: Turns without progress
   - `self.consecutive_hints`: Hint exchanges without play
   - `self.rounds_without_play`: Rounds since last card played
   - `self.last_hint_given`: Most recent hint to avoid immediate repeats

---

### AI Methods

#### 1. `receive_hint_from_participant(hint_type, hint_value, target_card_idx, actual_card)`
**When Called**: Participant gives hint about AI's card

**Process**:
1. Record hint in history
2. Update `ai_card_inferences` with new information
3. Check if AI now knows both color AND position
4. If complete information, check if card can be played
5. Return slot index if playable, False otherwise

**Critical Logic**:
```python
if card_info['color'] and card_info['position']:
    inferred_card = (card_info['color'], card_info['position'])
    if inferred_card in self.true_sequence:
        slot_idx = self.true_sequence.index(inferred_card)
        if self.sequence_knowledge[slot_idx] is None:
            return slot_idx  # CAN PLAY!
```

**Realistic Constraint**: AI only plays if it has received hints about BOTH color AND position

#### 2. `give_hint_to_participant()`
**When Called**: AI's turn

**Decision Tree**:
1. Update participant playable cards (with current cards!)
2. Calculate urgency scores
3. Check if stalling → need to hint back
4. Choose optimal hint strategy
5. Record hint in history
6. Return hint strategy or None

**Returns**:
```python
{
    'target_card': card_index,
    'hint_type': 'color' or 'position',
    'hint_value': actual value,
    'strategy': 'optimal'
}
```

#### 3. `should_hint_back_due_to_stall()`
**Purpose**: Detect game stalling

**Stall Conditions**:
- No card played in 2+ rounds
- 2+ consecutive hints without progress
- Sequence state unchanged for multiple turns

**Returns**: Boolean

**Why Important**: Prevents infinite hint loops where neither player can make progress

#### 4. `give_optimal_hint_to_participant()`
**Purpose**: Choose best possible hint for participant

**Strategy**:

1. **Identify Useful Cards**:
   ```python
   for i, card in enumerate(self.participant_cards):
       if card and card in self.true_sequence:
           if slot not already filled:
               useful_participant_cards.append((i, card, slot_idx))
   ```

2. **Prioritize by Urgency**:
   - Choose card with highest urgency score
   - Urgency based on game state (see `calculate_urgency_scores`)

3. **Choose Hint Type**:
   - Avoid repeating same hint type for same card
   - Alternate between color and position
   - Strategic variation

4. **Reset Counters**:
   - `consecutive_hints = 0`
   - `rounds_without_play = 0`

**Critical Feature**: Always hints about CURRENT participant cards, not old cards

#### 5. `update_participant_playable_cards()`
**Purpose**: Refresh list of participant cards that are in sequence

**Called**: Before each hint decision

**Why Important**: Participant cards change when replaced, so AI must track current cards

#### 6. `calculate_urgency_scores()`
**Purpose**: Assign priority to each sequence slot

**Scoring**:
- **+3**: Participant has playable card for this slot
- **+5**: Only 1 slot remaining (critical!)
- **0**: Slot already filled

**Result**: Array `[score_slot0, score_slot1, score_slot2]`

**Use**: Determines which card to hint about when multiple options available

#### 7. `can_play_card(card_idx)`
**Purpose**: Check if AI can play a card

**Requirements**:
- Must have received hints about BOTH color AND position
- Inferred card must be in true sequence
- Target slot must be empty

**Returns**: 
- Slot index (0-2) if can play
- `False` if cannot play

**Realistic Constraint**: Cannot play with incomplete information

#### 8. `play_card(card_idx, slot_idx)`
**Purpose**: Execute card play and update state

**Actions**:
1. Retrieve card info from inferences
2. Update `sequence_knowledge[slot_idx]`
3. Remove card from `ai_card_inferences` (card is gone)

#### 9. `update_after_participant_action(action_type, card_played=None, card_replaced=None)`
**Purpose**: Update AI's world model after participant acts

**Actions**:
- If card played and in sequence:
  - Update `sequence_knowledge`
  - Reset `rounds_without_play = 0`

**Why Important**: AI needs to know what's been played to avoid redundant hints

#### 10. `update_progress()`
**Purpose**: Track game progress for stall detection

**Actions**:
1. Record current sequence state
2. Keep last 3 states only (memory efficiency)
3. Increment `rounds_without_play`

**Use**: Enables stall detection by comparing recent states

#### 11. `choose_card_to_replace(computer_cards)`
**Purpose**: Intelligently choose which AI card to replace

**Strategy** (in priority order):

1. **Never Replace Hinted Cards**: Cards with any hints are valuable
   ```python
   hinted_indices = set(self.ai_card_inferences.keys())
   unhinted_indices = [i for i in available if i not in hinted_indices]
   if unhinted_indices:
       return random.choice(unhinted_indices)
   ```

2. **Replace Cards Known NOT in Sequence**: If AI knows both properties and it's not in sequence
   ```python
   if card_info['color'] and card_info['position']:
       inferred_card = (card_info['color'], card_info['position'])
       if inferred_card not in self.true_sequence:
           replaceable.append(idx)
   ```

3. **Don't Replace Anything**: If all cards are hinted and possibly useful
   ```python
   return None  # AI waits
   ```

**Why Optimal**: Preserves information gained from hints

---

## Game Flow

### Function: `run_single_trial(trial_number)`

#### Phase 1: Balanced Game Setup

**Sequence Creation**:
```python
true_sequence = random.sample(all_possible_cards, 3)
```
- Selects 3 unique cards
- No duplicates allowed

**Card Distribution** (BALANCED):
```python
num_participant_sequence_cards = random.randint(1, 2)
participant_sequence_cards = random.sample(true_sequence, num_participant_sequence_cards)
ai_sequence_cards = [card for card in true_sequence if card not in participant_sequence_cards]
```

**Distribution Options**:
- Participant: 1 sequence card, AI: 2 sequence cards (50% chance)
- Participant: 2 sequence cards, AI: 1 sequence card (50% chance)

**Why Important**: Ensures game is solvable and both players contribute

**Hand Construction**:
1. Give each player their sequence cards
2. Fill remaining slots with non-sequence cards
3. Shuffle each hand (so sequence cards not in predictable positions)

**Verification**:
```python
missing_cards = check_missing_sequence_cards(true_sequence, computer_cards, participant_cards, [])
if missing_cards:
    print("⚠️ ERROR: Missing cards after initial distribution")
```

#### Phase 2: Encoding (Study Phase)

**Process**:
1. Display instruction
2. Show each card in sequence for 0.8 seconds
3. Blank screen for 0.3 seconds between cards
4. Total study time: ~3.3 seconds

**Purpose**: Participant memorizes the target sequence

#### Phase 3: Gameplay Loop

**Loop Condition**: `while any(x is None for x in played_sequence)`
- Continues until all 3 slots filled

**Turn Structure**:

**Participant Turn** (action = h/p/r):

1. **Hint (h)**:
   - Select AI card (1-3)
   - Select hint type (1=Color, 2=Position)
   - Display hint message
   - AI receives hint and decides whether to play
   - If AI can play (knows both properties):
     - Play card immediately
     - Draw replacement (prioritizing missing sequence cards)
   - Else: AI keeps card

2. **Play (p)**:
   - Select which of own cards to play (blind!)
   - Select target slot (1-3)
   - Validate slot not taken
   - Place card in sequence
   - Update AI knowledge
   - Draw replacement card

3. **Replace (r)**:
   - Select card to replace
   - Draw new card (prioritizing missing sequence cards)
   - Update AI's participant_cards tracking

**AI Turn**:

1. **Get Hint Strategy**:
   - AI calculates optimal hint
   - If has useful hint: give hint to participant
   - Else: replace a card (avoiding hinted cards)

2. **Display Action**:
   - Show hint message (5 seconds)
   - Or show replacement message (2.5 seconds)
   - If stalling (rounds_without_play ≥ 2), display warning

3. **Update Progress Tracking**

**Turn Switch**: `participant_turn = not participant_turn`

#### Phase 4: Trial Completion

**Scoring**:
```python
correct = sum([played_sequence[i] == true_sequence[i] for i in range(3)])
```
- 0-3 points based on exact position matches

**Display Comparison**:
```
Target Sequence:  [Card1] [Card2] [Card3]
Your Sequence:    [Card1] [Card2] [Card3]
Score: 2/3
```

**Time Tracking**:
```python
trial_duration = trial_end_time - trial_start_time
minutes = int(trial_duration // 60)
seconds = int(trial_duration % 60)
time_formatted = f"{minutes}:{seconds:02d}"
```

**Return Value**:
```python
{
    'Trial': trial_number,
    'Score': correct,
    'Time_Seconds': round(trial_duration, 2),
    'Time_Formatted': time_formatted
}
```

---

### Main Game Flow (Two Trials)

**Steps**:
1. Get player name (text input)
2. Welcome message
3. Show instructions (H/P/R actions)
4. **Trial 1**: Run complete trial
5. Show Trial 1 summary
6. **Trial 2**: Run complete trial
7. Show Trial 2 summary
8. **Final Summary**: 
   - Individual scores
   - Total score (out of 6)
   - Average time
9. Save results to CSV
10. Thank you message

---

## Data Structures

### Stimuli Representation
**Format**: `(color, position)` tuple

**Example**: `("yellow", "up")`

**Valid Values**:
- Colors: "yellow", "blue", "cyan", "orange"
- Positions: "up", "down", "left", "right"

### Card Representation in Game

**Computer/Participant Cards**: `[card1, card2, card3]`
- Each card is `(color, position)` tuple or `None` if slot empty

**Played Sequence**: `[slot0, slot1, slot2]`
- Each slot is `(color, position)` tuple or `None` if not yet filled

### Hint Representation
```python
{
    'target_card': 0,  # Card index (0-2)
    'hint_type': 'color',  # 'color' or 'position'
    'hint_value': 'yellow',  # Actual color or position value
    'strategy': 'optimal'  # Strategy used
}
```

### Trial Results
```python
{
    'Trial': 1,
    'Score': 2,  # 0-3
    'Time_Seconds': 145.32,
    'Time_Formatted': "2:25"
}
```

---

## Key Design Decisions

### 1. Balanced Card Distribution
**Problem**: If one player has all sequence cards, the other player is useless

**Solution**: Randomly split sequence cards 1-2 or 2-1 between players

### 2. Missing Card Recovery
**Problem**: If a sequence card gets replaced, game becomes impossible

**Solution**: `draw_new_card()` prioritizes missing sequence cards when drawing replacements

### 3. Realistic AI Constraints
**Problem**: If AI is omniscient, game is too easy and unrealistic

**Solution**: AI can only play cards after receiving hints about BOTH color AND position

### 4. Stall Detection
**Problem**: Players can get stuck in infinite hint loops

**Solution**: Track rounds without progress and trigger AI hint-backs

### 5. Intelligent Card Replacement
**Problem**: AI might replace cards it has hints about

**Solution**: AI never replaces hinted cards unless certain they're not in sequence

### 6. Dynamic Participant Card Tracking
**Problem**: AI giving hints about cards participant replaced

**Solution**: AI updates `participant_cards` whenever participant replaces a card

### 7. Urgency Scoring
**Problem**: AI doesn't know which hints are most useful

**Solution**: Calculate urgency based on:
- Whether participant has playable cards
- How many slots remain
- Current game state

---

## Performance Considerations

### Localizer Task
- **Expected Runtime**: ~12-15 minutes
- **240 total trials**: 120 color + 120 position
- **Per trial time**: ~3-4 seconds average
  - 0.5-1.5s fixation
  - 1.0s response window
  - 0.6s feedback

### Practice Game
- **Expected Time per Trial**: 2-5 minutes
- **Depends on**:
  - Player speed
  - Number of turns (varies widely)
  - Strategy efficiency
- **Total for 2 trials**: 4-10 minutes

---
### Caveats
- At any given time, a card from the current sequence will be in play
- The AI always plays the correct card
- The AI only hints if you have cards that should be in the sequence
- The AI will wait for position and color information before placing a card
- If you hint at a card that's not in the sequence, the AI may ignore your hint (unless you've hinted each card in the sequence already -- then it will decide to replace)
## Conclusion

The optimal AI provides a challenging but fair partner that helps participants succeed while requiring strategic thinking and memory.

