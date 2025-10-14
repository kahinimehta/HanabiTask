from psychopy import visual, core, event
import os, random, time
from PIL import Image
import numpy as np

# =========================
#  SETUP
# =========================
win = visual.Window(size=[1280, 720], color='white', units='height', fullscr=False)
save_dir = "/Users/mehtaka/Desktop/Columbia/Nuttida_Lab/Collaboration_Code/Shapes"

if not os.path.exists(save_dir):
    raise ValueError(f"Shape folder not found: {save_dir}")

# --- safe image loader (fixes NSCFString issue) ---
def load_shape_image(win, img_path):
    try:
        img = Image.open(img_path).convert('RGB')
        temp_path = "_temp_rgb.png"
        img.save(temp_path)
        stim = visual.ImageStim(win, image=temp_path, size=(0.35, 0.35))
        return stim
    except Exception as e:
        print(f"⚠️ Failed to load {img_path}: {e}")
        return None

# =========================
#  STIMULI
# =========================
stimuli = [os.path.join(save_dir, f) for f in os.listdir(save_dir)
           if f.endswith(".png") and "_rotated" not in f]
rotated = [os.path.join(save_dir, f) for f in os.listdir(save_dir)
           if f.endswith("_rotated.png")]
stimuli.sort()
rotated.sort()

# =========================
#  BASIC VISUAL ELEMENTS
# =========================
instr = visual.TextStim(win, text="", color='black', height=0.035, wrapWidth=1.2)
fixation = visual.TextStim(win, text="+", color='black', height=0.08)
feedback_txt = visual.TextStim(win, text="", color='black', height=0.05)

def show_instructions(text):
    instr.text = text + "\n\nPress SPACE to continue."
    instr.draw()
    win.flip()
    event.clearEvents()
    event.waitKeys(keyList=['space'])

def jitter(min_t=0.5, max_t=1.5):
    return random.uniform(min_t, max_t)

def safe_wait(secs):
    timer = core.Clock()
    while timer.getTime() < secs:
        pass  # passive wait, doesn't call _dispatchWindowEvents()

# =========================
#  LOCALIZER TASK
# =========================
# 
def run_localizer():
    # --- setup ---
    start_time = time.time()  # record start in seconds since epoch
    colors = ["yellow", "blue", "cyan", "orange"]
    positions = ["up", "down", "left", "right"]
    base_reps = 15  # each unique color-position image appears 15× → 240 total

    # --- build master pool from filenames ---
    stim_pool = []
    for stim in stimuli:
        base = os.path.basename(stim).replace(".png", "")
        parts = base.split("_")  # e.g. ["yellow", "up", "square"]
        if len(parts) < 2:
            raise ValueError(f"Unexpected filename format: {base}")
        color, pos = parts[0], parts[1]
        if color not in colors or pos not in positions:
            print(f"⚠️ Skipping unrecognized stim: {base}")
            continue
        stim_pool += [(stim, color, pos)] * base_reps

    if not stim_pool:
        raise ValueError("Stimulus pool is empty — check filenames and paths.")

    random.shuffle(stim_pool)
    fallback_count = 0

    # --- helper functions ---
    def available_colors():
        """Return set of colors still available in the pool."""
        return set(c for _, c, _ in stim_pool)

    def available_positions():
        """Return set of positions still available in the pool."""
        return set(p for _, _, p in stim_pool)

    def draw_stim_from_pool(target_color=None, target_pos=None):
        """Draw and remove one stim from pool matching color/pos if possible, else fallback."""
        nonlocal stim_pool, fallback_count
        for i, (s, c, p) in enumerate(stim_pool):
            if (target_color is None or c == target_color) and (target_pos is None or p == target_pos):
                return stim_pool.pop(i)
        # fallback if exhausted
        fallback_count += 1
        return stim_pool.pop(0)

    # ---------- COLOR BLOCK ----------
    show_instructions(
        "Welcome to the first part!\n\n"
        "You'll see different color shapes appear one at a time.\n\n"
        "Perform a 1-back COLOR task:\n"
        "Press SPACE if the COLOR is the SAME as the previous one.\n\n"
        "Focus and respond as quickly and accurately as you can."
    )

    total_trials = 240
    n_color = total_trials // 2
    n_pos = total_trials - n_color

    # smart stochastic color sequence
    color_seq = []
    for i in range(n_color):
        avail = available_colors()
        if i > 0 and random.random() < 0.35 and color_seq[-1] in avail:
            color_seq.append(color_seq[-1])
        else:
            choices = [c for c in colors if c in avail and (not color_seq or c != color_seq[-1])]
            if not choices:
                # if all remaining are same color as last → force repeat
                choices = [color_seq[-1]]
            color_seq.append(random.choice(choices))

    color_trials = []
    for c in color_seq:
        s, c_out, p = draw_stim_from_pool(target_color=c)
        color_trials.append(("color", s, c_out, p))

    results = []
    clock = core.Clock()
    last_color = None

    for _, stim_path, color_now, pos in color_trials:
        fixation.draw()
        win.flip()
        safe_wait(random.uniform(0.5, 1.5))

        stim = load_shape_image(win, stim_path)
        offset = 0.3 # slight offset for position
        stim.pos = {
            "up": (0, offset),
            "down": (0, -offset),
            "left": (-offset, 0),
            "right": (offset, 0),
        }[pos]

        stim.draw()
        win.flip()
        clock.reset()
        event.clearEvents()
        keys = event.waitKeys(maxWait=1.0, keyList=["space"], timeStamped=clock)
        rt = keys[0][1] if keys else None
        pressed = keys is not None

        is_match = color_now == last_color if last_color is not None else False
        if is_match and pressed:
            feedback_text, correct = "Correct!", True
        elif is_match and not pressed:
            feedback_text, correct = "Miss!", False
        elif not is_match and pressed:
            feedback_text, correct = "False alarm!", False
        else:
            feedback_text, correct = "", True

        visual.TextStim(win, text=feedback_text, color="black", height=0.05).draw()
        win.flip()
        safe_wait(0.6)

        results.append({
            "block": "color",
            "stim": stim_path,
            "color": color_now,
            "position": pos,
            "match": is_match,
            "pressed": pressed,
            "rt": rt,
            "correct": correct,
        })
        last_color = color_now

    # ---------- BREAK ----------
    show_instructions(
        "Nice work!\n\n"
        "You can take a short break.\n\n"
        "Next up is the POSITION 1-back task.\n"
        "Press SPACE when you're ready to continue."
    )

    # ---------- POSITION BLOCK ----------
    show_instructions(
        "Now do the POSITION 1-back task.\n\n"
        "Press SPACE if the POSITION is the SAME as the previous one.\n\n"
        "Stay focused and respond quickly and accurately."
    )

    pos_seq = []
    for i in range(n_pos):
        avail = available_positions()
        if i > 0 and random.random() < 0.35 and pos_seq[-1] in avail:
            pos_seq.append(pos_seq[-1])
        else:
            choices = [p for p in positions if p in avail and (not pos_seq or p != pos_seq[-1])]
            if not choices:
                # if all remaining are same position as last → force repeat
                choices = [pos_seq[-1]]
            pos_seq.append(random.choice(choices))

    pos_trials = []
    for p in pos_seq:
        s, c, p_out = draw_stim_from_pool(target_pos=p)
        pos_trials.append(("position", s, c, p_out))

    last_pos = None
    for _, stim_path, color_now, pos in pos_trials:
        fixation.draw()
        win.flip()
        safe_wait(random.uniform(0.5, 1.5))

        stim = load_shape_image(win, stim_path)
        offset = 0.3 # slight offset for position
        stim.pos = {
            "up": (0, offset),
            "down": (0, -offset),
            "left": (-offset, 0),
            "right": (offset, 0),
        }[pos]

        stim.draw()
        win.flip()
        clock.reset()
        event.clearEvents()
        keys = event.waitKeys(maxWait=1.0, keyList=["space"], timeStamped=clock)
        rt = keys[0][1] if keys else None
        pressed = keys is not None

        is_match = pos == last_pos if last_pos is not None else False
        if is_match and pressed:
            feedback_text, correct = "Correct!", True
        elif is_match and not pressed:
            feedback_text, correct = "Miss!", False
        elif not is_match and pressed:
            feedback_text, correct = "False alarm!", False
        else:
            feedback_text, correct = "", True

        visual.TextStim(win, text=feedback_text, color="black", height=0.05).draw()
        win.flip()
        safe_wait(0.6)

        results.append({
            "block": "position",
            "stim": stim_path,
            "color": color_now,
            "position": pos,
            "match": is_match,
            "pressed": pressed,
            "rt": rt,
            "correct": correct,
        })
        last_pos = pos

    # ---------- SUMMARY ----------
    accuracy = np.mean([r["correct"] for r in results])
    color_acc = np.mean([r["correct"] for r in results if r["block"] == "color"])
    pos_acc = np.mean([r["correct"] for r in results if r["block"] == "position"])
    end_time = time.time()
    actual_runtime = (end_time - start_time) / 60  # convert seconds → minutes

    print(f"\n=== Runtime Summary ===")
    print(f"Actual run time: {actual_runtime:.2f} minutes")


    # count appearances per (color, position)
    from collections import Counter
    freq = Counter([(r["color"], r["position"]) for r in results])
    print("\n=== Stimulus Appearance Counts ===")
    for combo, n in sorted(freq.items()):
        print(f"{combo}: {n}")
    print(f"Total: {sum(freq.values())} (should be 240)")
    print(f"Fallbacks used: {fallback_count}")
    

    show_instructions(
        f"Awesome work!\n\n"
        f"That concludes the localizer.\n\n"
        f"Total accuracy: {accuracy*100:.1f}%\n"
        f"(Color: {color_acc*100:.1f}%, Position: {pos_acc*100:.1f}%)\n\n"
        f"(Stimulus pool fallback used {fallback_count} times — perfectly fine.)\n\n"
        "Next up: the practice memory game!"
    )


# =========================
#  PRACTICE GAME
# =========================
def run_practice():
    """Two-trial practice game with optimal AI and card circulation management"""
    
    import pandas as pd
    from datetime import datetime
    import time
    
    # =========================
    #  HELPER FUNCTIONS
    # =========================
    def parse_stim_filename(path):
        base = os.path.basename(path).replace(".png", "")
        parts = base.split("_")
        return parts[0], parts[1]

    def find_stim_file(color, pos):
        matches = [s for s in stimuli if f"{color}_" in os.path.basename(s) and f"_{pos}_" in os.path.basename(s)]
        if not matches:
            raise ValueError(f"No file for ({color}, {pos})")
        return matches[0]

    def draw_box(center, w=0.20, h=0.20, line="black", fill=None):
        visual.Rect(win, width=w, height=h, pos=center, lineColor=line, fillColor=fill, lineWidth=2).draw()

    def draw_card(center, color, pos, faceup=True, thumb=False):
        if not faceup:
            draw_box(center, w=0.20, h=0.20, fill="black")
            return
        try:
            stim_path = find_stim_file(color, pos)
            stim = load_shape_image(win, stim_path)
            stim.size = (0.15, 0.15) if not thumb else (0.10, 0.10)
            stim.pos = center
            stim.draw()
        except:
            # Fallback if image not found
            draw_box(center, w=0.20, h=0.20, fill="gray")

    def render_board_with_participant_cards(computer_cards, participant_cards, played_sequence, hint_text=None, show_participant_cards=False, selected_card=None):
        """Render board with proper variable scope"""
        win.clearBuffer()
        top_y, mid_y, bottom_y = 0.40, 0.10, -0.20
        xs = [-0.35, 0.0, 0.35]

        # Computer cards (visible to participant)
        for i, card in enumerate(computer_cards):
            center = (xs[i], top_y)
            draw_box(center, fill="#f0f0f0")
            if card:
                color, pos = card
                draw_card(center, color, pos, thumb=True)

        # Sequence slots (middle)
        for i, card in enumerate(played_sequence):
            center = (xs[i], mid_y)
            draw_box(center)
            if card:
                color, pos = card
                draw_card(center, color, pos)
            else:
                visual.TextStim(win, text="?", pos=center, color="black", height=0.07).draw()

        # Participant cards (hidden or visible)
        for i in range(3):
            center = (xs[i], bottom_y)
            if show_participant_cards and participant_cards[i]:
                # Show the actual card
                color, pos = participant_cards[i]
                draw_box(center, fill="#f0f0f0")
                draw_card(center, color, pos, thumb=True)
                # Highlight selected card
                if selected_card == i:
                    draw_box(center, w=0.22, h=0.22, line="red", fill=None)
            else:
                # Show as black box (hidden)
                draw_box(center, fill="black")

        if hint_text:
            visual.TextStim(win, text=hint_text, color="black", height=0.05, pos=(0, -0.45)).draw()
        win.flip()

    def choose_index(prompt, options=3):
        visual.TextStim(win, text=prompt, color="black", height=0.05, pos=(0, -0.45)).draw()
        win.flip()
        event.clearEvents()
        while True:
            keys = event.waitKeys(keyList=[str(i + 1) for i in range(options)] + ["escape"])
            if keys[0] == "escape":
                core.quit()
            return int(keys[0]) - 1

    def get_available_cards_for_replacement(all_cards_in_use, missing_sequence_cards):
        """FIXED: Get cards that aren't in use, prioritizing sequence cards if missing"""
        all_possible_cards = [parse_stim_filename(s) for s in stimuli]
        used_pairs = set(all_cards_in_use)
        available = [p for p in all_possible_cards if p not in used_pairs]
        
        # If there are missing sequence cards, return one of those first
        if missing_sequence_cards:
            for card in missing_sequence_cards:
                if card in available:
                    return card
        
        return random.choice(available) if available else None

    def draw_new_card(all_cards_in_use, missing_sequence_cards=[]):
        """FIXED: Draw a new card, prioritizing missing sequence cards"""
        card = get_available_cards_for_replacement(all_cards_in_use, missing_sequence_cards)
        if card is None:
            raise ValueError("No more cards available!")
        return card

    def check_missing_sequence_cards(true_sequence, computer_cards, participant_cards, played_sequence):
        """FIXED: Check which sequence cards are missing from circulation"""
        all_available_cards = set(computer_cards + participant_cards + [card for card in played_sequence if card])
        missing_cards = []
        
        for card in true_sequence:
            if card not in all_available_cards:
                missing_cards.append(card)
        
        return missing_cards

    def show_instructions_with_space(text, wait_time=0.1):
        """Show instructions with improved space key handling"""
        instr.text = text + "\n\nPress SPACE to continue."
        instr.draw()
        win.flip()
        
        # Clear any existing events and wait a bit
        event.clearEvents()
        core.wait(wait_time)
        
        # Wait for space with timeout and better handling
        while True:
            keys = event.getKeys(keyList=['space', 'escape'])
            if 'escape' in keys:
                core.quit()
            elif 'space' in keys:
                break
            core.wait(0.01)  # Small wait to prevent busy waiting

    def get_player_name():
        """Get player name input"""
        win.clearBuffer()
        visual.TextStim(win, text="Welcome to the Hanabi Practice Game!\n\nPlease enter your name:", 
                       color="black", height=0.05, pos=(0, 0.1)).draw()
        
        # Create text input field
        name_input = visual.TextStim(win, text="", color="blue", height=0.06, pos=(0, 0))
        current_name = ""
        
        while True:
            win.clearBuffer()
            visual.TextStim(win, text="Welcome to the Hanabi Practice Game!\n\nPlease enter your name:", 
                           color="black", height=0.05, pos=(0, 0.1)).draw()
            name_input.text = current_name
            name_input.draw()
            visual.TextStim(win, text="Press ENTER when done, BACKSPACE to delete", 
                           color="gray", height=0.03, pos=(0, -0.1)).draw()
            win.flip()
            
            keys = event.waitKeys()
            if keys:
                key = keys[0]
                if key == 'return':
                    if current_name.strip():
                        return current_name.strip()
                elif key == 'backspace':
                    current_name = current_name[:-1]
                elif key == 'escape':
                    core.quit()
                elif len(key) == 1 and key.isalnum() or key in ['space', '_', '-']:
                    current_name += key

    def save_results_to_spreadsheet(player_name, trial_results):
        """Simple CSV writing that definitely works"""
        import os
        
        filename = "player_accuracy.csv"
        
        # Check if file exists
        file_exists = os.path.exists(filename)
        
        # Open file in append mode
        with open(filename, 'a') as f:
            # Write header if file doesn't exist
            if not file_exists:
                f.write("Player_Name,Trial,Score,Time_Seconds,Time_Formatted,Timestamp\n")
            
            # Write each trial result
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for result in trial_results:
                line = f"{player_name},{result['Trial']},{result['Score']},{result['Time_Seconds']},{result['Time_Formatted']},{timestamp}\n"
                f.write(line)
                print(f"✅ Wrote: {line.strip()}")
        
        print(f"✅ Results saved to {filename}")

    # =========================
    #  REALISTIC OPTIMAL AI CLASS
    # =========================
    class OptimalAI:
        def __init__(self, true_sequence, participant_cards):
            # What the AI knows
            self.true_sequence = true_sequence
            self.participant_cards = participant_cards.copy()
            self.ai_cards = [None, None, None]  # AI doesn't know its own cards initially
            
            # AI's memory and planning
            self.hint_history = []  # All hints given/received
            self.sequence_knowledge = [None, None, None]  # What AI thinks is in each slot
            self.ai_card_inferences = {}  # Inferences about AI's own cards from hints
            self.participant_playable_cards = []  # Cards participant could play correctly
            self.urgency_scores = [0, 0, 0]  # How urgent each slot is
            
            # Progress tracking
            self.progress_history = []  # Track sequence state each turn
            self.play_history = []  # Track when cards were actually played
            self.stall_count = 0  # Count of turns without progress
            self.consecutive_hints = 0  # Count of consecutive hint exchanges
            self.rounds_without_play = 0  # Count rounds since last card was played
            self.last_hint_given = None  # Track last hint to avoid immediate repeats
            
        def receive_hint_from_participant(self, hint_type, hint_value, target_card_idx, actual_card):
            """AI receives a hint about its own card from participant"""
            self.hint_history.append({
                'type': 'received',
                'hint_type': hint_type,
                'hint_value': hint_value,
                'target_card': target_card_idx,
                'turn': len(self.hint_history)
            })
            
            # Update AI's knowledge about its own card
            if target_card_idx not in self.ai_card_inferences:
                self.ai_card_inferences[target_card_idx] = {'color': None, 'position': None, 'actual_card': actual_card}
            
            self.ai_card_inferences[target_card_idx][hint_type] = hint_value
            self.ai_card_inferences[target_card_idx]['actual_card'] = actual_card
            
            # Check if we now know enough to play this card
            return self.can_play_card(target_card_idx)
            
        def give_hint_to_participant(self):
            """OPTIMAL: AI gives the best possible hint to participant"""
            # Update participant playable cards with CURRENT cards
            self.update_participant_playable_cards()
            
            # Calculate urgency for each slot
            self.calculate_urgency_scores()
            
            # Check if we should hint back due to stalling
            if self.should_hint_back_due_to_stall():
                return self.give_optimal_hint_to_participant()
            
            # Choose best hint strategy
            hint_strategy = self.give_optimal_hint_to_participant()
            
            if hint_strategy:
                self.hint_history.append({
                    'type': 'given',
                    'hint_type': hint_strategy['hint_type'],
                    'hint_value': hint_strategy['hint_value'],
                    'target_card': hint_strategy['target_card'],
                    'turn': len(self.hint_history)
                })
                self.consecutive_hints += 1
                self.last_hint_given = hint_strategy
                return hint_strategy
            
            return None
            
        def should_hint_back_due_to_stall(self):
            """Determine if AI should hint back due to stalling"""
            # Check if we haven't played a card in over 2 rounds
            if self.rounds_without_play >= 2:
                return True
            
            # Also check if we've been exchanging hints without progress
            if self.consecutive_hints >= 2:
                # Check if there's been no progress in sequence
                if len(self.progress_history) >= 2:
                    last_progress = self.progress_history[-1]
                    second_last_progress = self.progress_history[-2]
                    if last_progress == second_last_progress:
                        return True
            
            return False
            
        def give_optimal_hint_to_participant(self):
            """OPTIMAL: Give the best possible hint to participant about their CURRENT cards"""
            # Find participant cards that could be useful (CURRENT cards)
            useful_participant_cards = []
            for i, card in enumerate(self.participant_cards):
                if card and card in self.true_sequence:
                    slot_idx = self.true_sequence.index(card)
                    if self.sequence_knowledge[slot_idx] is None:
                        useful_participant_cards.append((i, card, slot_idx))
            
            if not useful_participant_cards:
                return None
            
            # OPTIMAL: Choose the most urgent card
            most_urgent = max(useful_participant_cards, key=lambda x: self.urgency_scores[x[2]])
            card_idx, card, slot_idx = most_urgent
            
            # OPTIMAL: Choose hint type strategically - avoid immediate repeats
            if self.last_hint_given and self.last_hint_given['target_card'] == card_idx:
                # Different hint type from last time
                hint_type = 'position' if self.last_hint_given['hint_type'] == 'color' else 'color'
            else:
                # Choose random hint type
                hint_type = random.choice(['color', 'position'])
            
            hint_value = card[0] if hint_type == 'color' else card[1]
            
            self.consecutive_hints = 0  # Reset counter when giving strategic hint
            self.rounds_without_play = 0  # Reset stall counter
            
            return {
                'target_card': card_idx,
                'hint_type': hint_type,
                'hint_value': hint_value,
                'strategy': 'optimal'
            }
            
        def update_participant_playable_cards(self):
            """Update which participant cards can be played correctly (CURRENT cards)"""
            self.participant_playable_cards = []
            for i, card in enumerate(self.participant_cards):
                if card and card in self.true_sequence:
                    slot_idx = self.true_sequence.index(card)
                    if self.sequence_knowledge[slot_idx] is None:
                        self.participant_playable_cards.append((i, card, slot_idx))
        
        def calculate_urgency_scores(self):
            """Calculate how urgent each slot is based on game state"""
            self.urgency_scores = [0, 0, 0]
            
            # Higher urgency if participant has playable cards for that slot
            for card_idx, card, slot_idx in self.participant_playable_cards:
                self.urgency_scores[slot_idx] += 3
                
            # Higher urgency if we're running out of turns
            remaining_slots = sum(1 for x in self.sequence_knowledge if x is None)
            if remaining_slots <= 1:
                for i in range(3):
                    if self.sequence_knowledge[i] is None:
                        self.urgency_scores[i] += 5
                        
            # 0 urgency for slots we already know
            for i in range(3):
                if self.sequence_knowledge[i] is not None:
                    self.urgency_scores[i] = 0
        
        def can_play_card(self, card_idx):
            """REALISTIC: Check if AI can play a card based on received hints ONLY"""
            if card_idx not in self.ai_card_inferences:
                return False
                
            card_info = self.ai_card_inferences[card_idx]
            if card_info['color'] and card_info['position']:
                # We know both color and position
                inferred_card = (card_info['color'], card_info['position'])
                if inferred_card in self.true_sequence:
                    slot_idx = self.true_sequence.index(inferred_card)
                    # Check if slot is actually empty before playing
                    if self.sequence_knowledge[slot_idx] is None:
                        return slot_idx
            return False
            
        def play_card(self, card_idx, slot_idx):
            """AI plays a card and updates its knowledge"""
            if card_idx in self.ai_card_inferences:
                card_info = self.ai_card_inferences[card_idx]
                played_card = (card_info['color'], card_info['position'])
                self.sequence_knowledge[slot_idx] = played_card
                del self.ai_card_inferences[card_idx]
                
        def update_after_participant_action(self, action_type, card_played=None, card_replaced=None):
            """Update AI knowledge after participant action"""
            if action_type == 'play' and card_played:
                # Only update if the card is actually in the true sequence
                if card_played in self.true_sequence:
                    slot_idx = self.true_sequence.index(card_played)
                    self.sequence_knowledge[slot_idx] = card_played
                    # Reset stall counter when card is played
                    self.rounds_without_play = 0
                    
        def update_progress(self):
            """Track progress in the sequence"""
            current_state = tuple(self.sequence_knowledge)
            self.progress_history.append(current_state)
            
            # Keep only last 3 states to check for stalls
            if len(self.progress_history) > 3:
                self.progress_history = self.progress_history[-3:]
            
            # Track rounds without playing cards
            self.rounds_without_play += 1
        
        def choose_card_to_replace(self, computer_cards):
            """OPTIMAL: Choose which AI card to replace, avoiding hinted cards"""
            available_indices = [i for i, card in enumerate(computer_cards) if card]
            
            if not available_indices:
                return None
            
            # NEVER replace cards we have hints about
            hinted_indices = set(self.ai_card_inferences.keys())
            unhinted_indices = [i for i in available_indices if i not in hinted_indices]
            
            # If we have unhinted cards, always replace those first
            if unhinted_indices:
                return random.choice(unhinted_indices)
            
            # If all cards are hinted, replace the one with least information
            # that we know is NOT in the sequence
            replaceable = []
            for idx in available_indices:
                card_info = self.ai_card_inferences.get(idx)
                if card_info:
                    # If we know both color and position
                    if card_info['color'] and card_info['position']:
                        inferred_card = (card_info['color'], card_info['position'])
                        # Only replace if we KNOW it's not in the sequence
                        if inferred_card not in self.true_sequence:
                            replaceable.append(idx)
            
            if replaceable:
                return random.choice(replaceable)
            
            # Last resort: don't replace anything (return None)
            return None

    def run_single_trial(trial_number):
        """Run a single trial and return results"""
        trial_start_time = time.time()
        
        # =========================
        #  BALANCED GAME SETUP
        # =========================
        
        # Create a random 3-card sequence with NO duplicates
        all_possible_cards = [parse_stim_filename(s) for s in stimuli]
        true_sequence = random.sample(all_possible_cards, 3)
        
        # Ensure no duplicates in true sequence
        while len(set(true_sequence)) != len(true_sequence):
            true_sequence = random.sample(all_possible_cards, 3)
        
        # BALANCED: Distribute sequence cards between both players
        # Participant gets 1-2 sequence cards, AI gets the remaining ones
        num_participant_sequence_cards = random.randint(1, 2)
        participant_sequence_cards = random.sample(true_sequence, num_participant_sequence_cards)
        ai_sequence_cards = [card for card in true_sequence if card not in participant_sequence_cards]
        
        print(f"🎮 Sequence distribution:")
        print(f"   Participant gets: {participant_sequence_cards}")
        print(f"   AI gets: {ai_sequence_cards}")
        
        # Initialize hands with sequence cards distributed
        all_used = set(true_sequence)
        computer_cards = []
        participant_cards = []
        
        # Give AI its sequence cards first
        for card in ai_sequence_cards:
            computer_cards.append(card)
        
        # Fill AI's remaining slots with non-sequence cards
        while len(computer_cards) < 3:
            new_card = draw_new_card(list(all_used), [])
            computer_cards.append(new_card)
            all_used.add(new_card)
        
        # Shuffle AI cards so sequence cards aren't in predictable positions
        random.shuffle(computer_cards)
        
        # Give participant their sequence cards
        for card in participant_sequence_cards:
            participant_cards.append(card)
        
        # Fill participant's remaining slots with non-sequence cards
        while len(participant_cards) < 3:
            new_card = draw_new_card(list(all_used), [])
            participant_cards.append(new_card)
            all_used.add(new_card)
        
        # Shuffle participant cards
        random.shuffle(participant_cards)
        
        # Verify distribution is correct
        missing_cards = check_missing_sequence_cards(true_sequence, computer_cards, participant_cards, [])
        if missing_cards:
            print(f"⚠️ ERROR: Missing cards after initial distribution: {missing_cards}")
        
        played_sequence = [None, None, None]
        turn_count = 0
        participant_turn = random.choice([True, False])

        # Initialize optimal AI
        ai = OptimalAI(true_sequence, participant_cards)

        # =========================
        #  ENCODING PHASE
        # =========================
        show_instructions_with_space(f"Trial {trial_number}\n\nNow let's study the target sequence.\n\nWatch carefully!")
        
        xs = [-0.35, 0.0, 0.35]
        for i, (color, pos) in enumerate(true_sequence):
            draw_box((xs[i], 0.1))
            draw_card((xs[i], 0.1), color, pos)
            win.flip()
            safe_wait(0.8)
            win.flip()
            safe_wait(0.3)

        show_instructions_with_space("Perfect! Now let's play.\n\nWork with your AI partner to rebuild this exact sequence!")

        # =========================
        #  REALISTIC OPTIMAL GAMEPLAY
        # =========================
        while any(x is None for x in played_sequence):
            turn_count += 1
            
            # Check for missing sequence cards
            missing_cards = check_missing_sequence_cards(true_sequence, computer_cards, participant_cards, played_sequence)
            
            if participant_turn:
                # ===== PARTICIPANT TURN =====
                render_board_with_participant_cards(computer_cards, participant_cards, played_sequence, "Your turn: (H)int, (P)lay, (R)eplace")
                keys = event.waitKeys(keyList=["h", "p", "r", "escape"])
                if keys[0] == "escape":
                    core.quit()
                action = keys[0]

                if action == "h":
                    # Participant gives hint to AI
                    render_board_with_participant_cards(computer_cards, participant_cards, played_sequence, "Select an AI card to hint about (1-3):")
                    target_idx = choose_index("Which AI card?")
                    
                    if computer_cards[target_idx] is None:
                        render_board_with_participant_cards(computer_cards, participant_cards, played_sequence, "That card is gone!")
                        safe_wait(1)
                        continue

                    hint_type_idx = choose_index("1 = Color, 2 = Position", options=2)
                    hint_type = "color" if hint_type_idx == 0 else "position"
                    color, pos = computer_cards[target_idx]
                    hint_value = color if hint_type == "color" else pos
                    
                    render_board_with_participant_cards(computer_cards, participant_cards, played_sequence, f"You hint: 'Card {target_idx+1} has {hint_value.upper()}' ({hint_type})")
                    safe_wait(1.5)

                    # AI receives hint and decides what to do BASED ON HINT KNOWLEDGE ONLY
                    can_play_slot = ai.receive_hint_from_participant(hint_type, hint_value, target_idx, (color, pos))
                    
                    # REALISTIC: Check if AI can play the card (knows both color AND position)
                    if can_play_slot is not False and played_sequence[can_play_slot] is None:
                        # AI CAN play the card - PLAY IT!
                        played_sequence[can_play_slot] = (color, pos)
                        computer_cards[target_idx] = None
                        ai.play_card(target_idx, can_play_slot)
                        render_board_with_participant_cards(computer_cards, participant_cards, played_sequence, f"AI plays {color.upper()} {pos.upper()}!")
                        safe_wait(2.5)
                        
                        # Reset AI stall counter
                        ai.rounds_without_play = 0
                        
                        # Draw replacement card - prioritize missing sequence cards
                        all_cards_in_use = computer_cards + participant_cards + [card for card in played_sequence if card]
                        new_card = draw_new_card(all_cards_in_use, missing_cards)
                        computer_cards[target_idx] = new_card
                        
                    else:
                        # REALISTIC: AI doesn't have enough information yet - keep the card
                        render_board_with_participant_cards(computer_cards, participant_cards, played_sequence, "AI acknowledges the hint and keeps the card.")
                        safe_wait(2.5)

                elif action == "p":
                    # Participant plays card
                    render_board_with_participant_cards(computer_cards, participant_cards, played_sequence, "Choose which card to play (1-3):", show_participant_cards=False)
                    card_idx = choose_index("Which card?")
                    
                    if participant_cards[card_idx] is None:
                        render_board_with_participant_cards(computer_cards, participant_cards, played_sequence, "That slot is empty!")
                        safe_wait(1)
                        continue
                    
                    render_board_with_participant_cards(computer_cards, participant_cards, played_sequence, f"Choose which slot (1-3):", show_participant_cards=False, selected_card=card_idx)
                    slot_idx = choose_index("Which slot?")
                    
                    if played_sequence[slot_idx] is not None:
                        render_board_with_participant_cards(computer_cards, participant_cards, played_sequence, "That slot is taken!")
                        safe_wait(1)
                        continue
                    
                    played_card = participant_cards[card_idx]
                    played_sequence[slot_idx] = played_card
                    participant_cards[card_idx] = None
                    
                    # Update AI knowledge
                    ai.update_after_participant_action('play', card_played=played_card)
                    
                    render_board_with_participant_cards(computer_cards, participant_cards, played_sequence, "You played a card!")
                    safe_wait(1.2)
                    
                    # Draw replacement card - prioritize missing sequence cards
                    all_cards_in_use = computer_cards + participant_cards + [card for card in played_sequence if card]
                    new_card = draw_new_card(all_cards_in_use, missing_cards)
                    participant_cards[card_idx] = new_card

                elif action == "r":
                    # Participant replaces card
                    render_board_with_participant_cards(computer_cards, participant_cards, played_sequence, "Choose which card to replace (1-3):", show_participant_cards=False)
                    replace_idx = choose_index("Which card?")
                    
                    if participant_cards[replace_idx]:
                        old_card = participant_cards[replace_idx]
                        # Draw replacement card - prioritize missing sequence cards
                        all_cards_in_use = computer_cards + participant_cards + [card for card in played_sequence if card]
                        new_card = draw_new_card(all_cards_in_use, missing_cards)
                        participant_cards[replace_idx] = new_card
                        
                        # Update AI knowledge
                        ai.participant_cards = participant_cards.copy()
                        
                        render_board_with_participant_cards(computer_cards, participant_cards, played_sequence, "You replaced a card!")
                        safe_wait(1.2)

            else:
                # ===== OPTIMAL AI TURN (FIXED!) =====
                hint_strategy = ai.give_hint_to_participant()
                
                if hint_strategy:
                    hint_idx = hint_strategy['target_card']
                    hint_type = hint_strategy['hint_type']
                    hint_value = hint_strategy['hint_value']
                    strategy = hint_strategy.get('strategy', 'normal')
                    
                    if ai.rounds_without_play >= 2:
                        render_board_with_participant_cards(computer_cards, participant_cards, played_sequence, f"AI hints: 'Your card {hint_idx+1} has {hint_value.upper()}' ({hint_type})\n[No cards played in {ai.rounds_without_play} rounds!]")
                    else:
                        render_board_with_participant_cards(computer_cards, participant_cards, played_sequence, f"AI hints: 'Your card {hint_idx+1} has {hint_value.upper()}' ({hint_type})")
                    safe_wait(5.0)
                else:
                    # FIXED: AI intelligently replaces a card, avoiding hinted cards
                    replace_idx = ai.choose_card_to_replace(computer_cards)
                    
                    if replace_idx is not None:
                        # Get replacement card
                        all_cards_in_use = computer_cards + participant_cards + [card for card in played_sequence if card]
                        new_card = draw_new_card(all_cards_in_use, missing_cards)
                        
                        # Log what's being replaced
                        old_card = computer_cards[replace_idx]
                        print(f"🤖 AI replacing card at position {replace_idx}: {old_card} with {new_card}")
                        
                        computer_cards[replace_idx] = new_card
                        render_board_with_participant_cards(computer_cards, participant_cards, played_sequence, f"AI replaced an unhinted card at position {replace_idx+1}.")
                    else:
                        # AI has hints about all cards, but not enough info to know which card (i.e -- not color and position)  -- so just wait
                        render_board_with_participant_cards(computer_cards, participant_cards, played_sequence, "AI is waiting for more information.")
                    
                    safe_wait(2.5)
                
                # Update progress tracking
                ai.update_progress()

            # Switch turns
            participant_turn = not participant_turn

        # =========================
        #  TRIAL COMPLETION
        # =========================
        trial_end_time = time.time()
        trial_duration = trial_end_time - trial_start_time
        
        correct = sum([played_sequence[i] == true_sequence[i] for i in range(3)])
        score_text = f"Score: {correct}/3"
        
        render_board_with_participant_cards(computer_cards, participant_cards, played_sequence, f"Trial {trial_number} complete!")
        safe_wait(3.0)

        # Show comparison
        win.clearBuffer()
        win.flip()
        safe_wait(0.1)

        win.clearBuffer()
        
        # True sequence (top)
        for i, (color, pos) in enumerate(true_sequence):
            draw_box((xs[i], 0.25))
            draw_card((xs[i], 0.25), color, pos)
        visual.TextStim(win, text="Target Sequence", color="black", height=0.05, pos=(0, 0.45)).draw()

        # Played sequence (bottom)
        for i, card in enumerate(played_sequence):
            if card:
                color, pos = card
                draw_box((xs[i], -0.05))
                draw_card((xs[i], -0.05), color, pos)
        visual.TextStim(win, text="Your Sequence", color="black", height=0.05, pos=(0, -0.25)).draw()

        visual.TextStim(win, text=score_text, color="black", height=0.06, pos=(0, -0.45)).draw()
        
        win.flip()
        safe_wait(4)
        
        # Format time
        minutes = int(trial_duration // 60)
        seconds = int(trial_duration % 60)
        time_formatted = f"{minutes}:{seconds:02d}"
        
        return {
            'Trial': trial_number,
            'Score': correct,
            'Time_Seconds': round(trial_duration, 2),
            'Time_Formatted': time_formatted
        }

    # =========================
    #  MAIN GAME FLOW
    # =========================
    
    # Get player name
    player_name = get_player_name()
    
    # Show welcome message
    show_instructions_with_space(f"Welcome, {player_name}!\n\nYou will play 2 practice trials.")
    
    # Show instructions
    show_instructions_with_space(
        "HOW TO PLAY:\n\n"
        "• Press H - Give a HINT about your partner's cards\n"
        "• Press P - PLAY one of your cards\n"
        "• Press R - REPLACE one of your cards"
    )
    
    # Run two trials
    trial_results = []
    
    for trial_num in range(1, 3):
        if trial_num > 1:
            show_instructions_with_space(f"Ready for Trial {trial_num}?")
        
        trial_result = run_single_trial(trial_num)
        trial_results.append(trial_result)
        
        show_instructions_with_space(
            f"Trial {trial_num} Summary:\n\n"
            f"Score: {trial_result['Score']}/3\n"
            f"Time: {trial_result['Time_Formatted']}"
        )
    
    # Show final summary
    total_score = sum(r['Score'] for r in trial_results)
    avg_time = sum(r['Time_Seconds'] for r in trial_results) / len(trial_results)
    avg_minutes = int(avg_time // 60)
    avg_seconds = int(avg_time % 60)
    
    show_instructions_with_space(
        f"🎉 Practice Complete!\n\n"
        f"Trial 1: {trial_results[0]['Score']}/3 ({trial_results[0]['Time_Formatted']})\n"
        f"Trial 2: {trial_results[1]['Score']}/3 ({trial_results[1]['Time_Formatted']})\n\n"
        f"Total Score: {total_score}/6\n"
        f"Avg Time: {avg_minutes}:{avg_seconds:02d}\n\n"
        f"Great work, {player_name}!"
    )
    
    # Save results to spreadsheet
    save_results_to_spreadsheet(player_name, trial_results)
    
    show_instructions_with_space("Your results have been saved!\n\nThank you!")


# run_localizer() # uncomment to run the localizer
run_practice()


win.close()
core.quit()

