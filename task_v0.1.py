from psychopy import visual, core, event
import os, random, time
from PIL import Image
import numpy as np
import csv
from datetime import datetime

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
mouse = event.Mouse(win=win)

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
    """Two-trial practice game with optimal AI, mouse-based interface, and turn-by-turn logging"""
    
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

    def draw_box(center, w=0.20, h=0.20, line="black", fill=None, linewidth=2):
        visual.Rect(win, width=w, height=h, pos=center, lineColor=line, fillColor=fill, lineWidth=linewidth).draw()

    def draw_card(center, color, pos, faceup=True, thumb=False, hint_info=None):
        """Draw a card with optional hint visualization"""
        if not faceup:
            # If we have hint info, show it on the black card
            if hint_info and (hint_info['color'] or hint_info['position']):
                # Draw colored box if color is known
                if hint_info['color']:
                    color_map = {'yellow': '#FFD700', 'blue': '#4169E1', 
                                'cyan': '#00CED1', 'orange': '#FF8C00'}
                    fill_color = color_map.get(hint_info['color'], 'gray')
                    draw_box(center, w=0.20, h=0.20, fill=fill_color)
                else:
                    draw_box(center, w=0.20, h=0.20, fill="black")
                
                # Draw arrow if position is known
                if hint_info['position']:
                    arrow_map = {
                        'up': '^', 'down': 'v', 'left': '<', 'right': '>'
                    }
                    arrow = arrow_map.get(hint_info['position'], '?')
                    # Black outline for visibility (draw first, thicker)
                    for dx, dy in [(-0.003, 0), (0.003, 0), (0, -0.003), (0, 0.003),
                                   (-0.002, -0.002), (0.002, 0.002), (-0.002, 0.002), (0.002, -0.002)]:
                        visual.TextStim(win, text=arrow, pos=(center[0]+dx, center[1]+dy), 
                                      color='black', height=0.12, bold=True).draw()
                    # White arrow on top
                    visual.TextStim(win, text=arrow, pos=center, color='white', 
                                  height=0.12, bold=True).draw()
            else:
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

    def render_board(computer_cards, participant_cards, played_sequence, hint_text=None, 
                    participant_hints=None, highlight_cards=None, buttons=None):
        """Render the complete game board with persistent display"""
        win.clearBuffer()
        top_y, mid_y, bottom_y = 0.25, 0.05, -0.15
        xs = [-0.30, 0.0, 0.30]

        # Computer cards (visible to participant) - TOP
        for i, card in enumerate(computer_cards):
            center = (xs[i], top_y)
            is_highlighted = highlight_cards and ('ai', i) in highlight_cards
            if is_highlighted:
                draw_box(center, w=0.24, h=0.24, line="red", linewidth=4, fill=None)
            draw_box(center, fill="#f0f0f0")
            if card:
                color, pos = card
                draw_card(center, color, pos, thumb=True)

        # Sequence slots (middle) - CENTER
        for i, card in enumerate(played_sequence):
            center = (xs[i], mid_y)
            is_highlighted = highlight_cards and ('slot', i) in highlight_cards
            if is_highlighted:
                draw_box(center, w=0.24, h=0.24, line="red", linewidth=4, fill=None)
            draw_box(center)
            if card:
                color, pos = card
                draw_card(center, color, pos)
            else:
                visual.TextStim(win, text="?", pos=center, color="black", height=0.07).draw()

        # Participant cards (with hints) - BOTTOM
        for i in range(3):
            center = (xs[i], bottom_y)
            is_highlighted = highlight_cards and ('participant', i) in highlight_cards
            if is_highlighted:
                draw_box(center, w=0.24, h=0.24, line="red", linewidth=4, fill=None)
            
            if participant_cards[i]:
                hint_info = participant_hints.get(i, {'color': None, 'position': None}) if participant_hints else None
                draw_card(center, None, None, faceup=False, hint_info=hint_info)
            else:
                draw_box(center, fill="#333333")  # Empty slot (darker gray)

        # Draw buttons if provided
        if buttons:
            for button_name, rect in buttons.items():
                center_x = (rect['left'] + rect['right']) / 2
                center_y = (rect['bottom'] + rect['top']) / 2
                width = rect['right'] - rect['left']
                height = rect['top'] - rect['bottom']
                
                # Button background
                visual.Rect(win, width=width, height=height, pos=(center_x, center_y),
                          fillColor='lightgray', lineColor='black', lineWidth=2).draw()
                # Button text
                visual.TextStim(win, text=button_name, pos=(center_x, center_y),
                              color='black', height=0.03, bold=True).draw()

        # Hint text at bottom
        if hint_text:
            visual.TextStim(win, text=hint_text, color="black", height=0.03, pos=(0, -0.35), wrapWidth=1.0).draw()
        
        win.flip()

    def wait_for_click_on_region(regions, clock=None):
        """Wait for mouse click on one of the defined regions. Returns (region_name, RT)"""
        mouse.clickReset()
        start_time = core.Clock()
        start_time.reset()
        
        while True:
            if mouse.getPressed()[0]:  # Left click
                pos = mouse.getPos()
                rt = start_time.getTime()  # Always return RT
                
                for region_name, bounds in regions.items():
                    if (bounds['left'] <= pos[0] <= bounds['right'] and
                        bounds['bottom'] <= pos[1] <= bounds['top']):
                        # Wait for release
                        while mouse.getPressed()[0]:
                            pass
                        return region_name, rt
            
            # Check for escape
            keys = event.getKeys(['escape'])
            if 'escape' in keys:
                core.quit()
            
            core.wait(0.01)

    def get_card_regions():
        """Define clickable regions for cards"""
        xs = [-0.30, 0.0, 0.30]
        top_y, mid_y, bottom_y = 0.25, 0.05, -0.15
        card_w, card_h = 0.20, 0.20
        
        regions = {}
        
        # AI cards (top)
        for i, x in enumerate(xs):
            regions[('ai', i)] = {
                'left': x - card_w/2, 'right': x + card_w/2,
                'bottom': top_y - card_h/2, 'top': top_y + card_h/2
            }
        
        # Sequence slots (middle)
        for i, x in enumerate(xs):
            regions[('slot', i)] = {
                'left': x - card_w/2, 'right': x + card_w/2,
                'bottom': mid_y - card_h/2, 'top': mid_y + card_h/2
            }
        
        # Participant cards (bottom)
        for i, x in enumerate(xs):
            regions[('participant', i)] = {
                'left': x - card_w/2, 'right': x + card_w/2,
                'bottom': bottom_y - card_h/2, 'top': bottom_y + card_h/2
            }
        
        return regions

    def get_button_regions(button_names):
        """Create button regions for actions"""
        button_y = -0.25
        button_spacing = 0.20
        button_width = 0.15
        button_height = 0.06
        
        num_buttons = len(button_names)
        start_x = -(num_buttons - 1) * button_spacing / 2
        
        buttons = {}
        for i, name in enumerate(button_names):
            center_x = start_x + i * button_spacing
            buttons[name] = {
                'left': center_x - button_width/2,
                'right': center_x + button_width/2,
                'bottom': button_y - button_height/2,
                'top': button_y + button_height/2
            }
        
        return buttons

    def get_available_cards_for_replacement(all_cards_in_use, missing_sequence_cards):
        """Get cards that aren't in use, prioritizing sequence cards if missing"""
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
        """Draw a new card, prioritizing missing sequence cards"""
        card = get_available_cards_for_replacement(all_cards_in_use, missing_sequence_cards)
        if card is None:
            raise ValueError("No more cards available!")
        return card

    def check_missing_sequence_cards(true_sequence, computer_cards, participant_cards, played_sequence):
        """Check which sequence cards are missing from circulation"""
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
                elif len(key) == 1 and key.isalnum():
                    current_name += key
                elif key == 'space':
                    current_name += ' '
                elif key in ['_', '-']:
                    current_name += key

    def save_turn_log(player_name, trial_number, turn_logs):
        """Save detailed turn-by-turn log to CSV"""
        filename = "turn_by_turn_log.csv"
        file_exists = os.path.exists(filename)
        
        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Player_Name', 'Trial', 'Turn', 'Player', 'Action', 'Details', 'RT_Seconds', 'Timestamp'])
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for log in turn_logs:
                writer.writerow([
                    player_name,
                    trial_number,
                    log['turn'],
                    log['player'],
                    log['action'],
                    log['details'],
                    round(log['rt'], 3) if log['rt'] else '',
                    timestamp
                ])
        
        print(f"✅ Turn log saved to {filename}")

    def save_results_to_spreadsheet(player_name, trial_results):
        """Save trial results to CSV"""
        filename = "player_accuracy.csv"
        file_exists = os.path.exists(filename)
        
        with open(filename, 'a') as f:
            if not file_exists:
                f.write("Player_Name,Trial,Score,Time_Seconds,Time_Formatted,Timestamp\n")
            
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
                # Choose most informative hint type
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
                        
            # Lower urgency for slots we already know
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

    def run_single_trial(trial_number, player_name):
        """Run a single trial and return results"""
        trial_start_time = time.time()
        turn_logs = []  # Store turn-by-turn actions
        
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
        participant_hints = {0: {'color': None, 'position': None},
                           1: {'color': None, 'position': None},
                           2: {'color': None, 'position': None}}

        # Initialize optimal AI
        ai = OptimalAI(true_sequence, participant_cards)

        # =========================
        #  ENCODING PHASE (SEQUENTIAL)
        # =========================
        show_instructions_with_space(f"Trial {trial_number}\n\nNow let's study the target sequence.\n\nWatch carefully!\n\nCards will appear one by one.")
        
        xs = [-0.30, 0.0, 0.30]
        # Show cards sequentially: 1, then 1+2, then 1+2+3
        for num_cards in range(1, 4):
            win.clearBuffer()
            for i in range(num_cards):
                color, pos = true_sequence[i]
                draw_box((xs[i], 0.1))
                draw_card((xs[i], 0.1), color, pos)
            win.flip()
            safe_wait(1.5)  # Show for 1.5 seconds

        show_instructions_with_space("Perfect! Now let's play.\n\nClick on cards to interact with them!")

        # =========================
        #  MOUSE-BASED GAMEPLAY
        # =========================
        card_regions = get_card_regions()
        
        while any(x is None for x in played_sequence):
            turn_count += 1
            
            # Check for missing sequence cards
            missing_cards = check_missing_sequence_cards(true_sequence, computer_cards, participant_cards, played_sequence)
            
            if participant_turn:
                # ===== PARTICIPANT TURN =====
                # Show action buttons
                action_buttons = get_button_regions(['HINT', 'PLAY', 'REPLACE'])
                render_board(computer_cards, participant_cards, played_sequence,
                           "Your turn! Click an action:", participant_hints, buttons=action_buttons)
                
                # Wait for action selection
                all_regions = {**action_buttons}
                action, action_rt = wait_for_click_on_region(all_regions)
                
                if action == "HINT":
                    # Step 1: Select AI card
                    render_board(computer_cards, participant_cards, played_sequence,
                               "Click on an AI card (top row) to hint about:", participant_hints)
                    
                    ai_regions = {k: v for k, v in card_regions.items() if k[0] == 'ai'}
                    selected, card_rt = wait_for_click_on_region(ai_regions)
                    target_idx = selected[1]
                    
                    if computer_cards[target_idx] is None:
                        render_board(computer_cards, participant_cards, played_sequence,
                                   "That card is gone! Try again.", participant_hints)
                        safe_wait(1)
                        continue
                    
                    # Step 2: Select hint type
                    hint_buttons = get_button_regions(['COLOR', 'POSITION'])
                    render_board(computer_cards, participant_cards, played_sequence,
                               f"Hint about AI card {target_idx+1}: Click COLOR or POSITION",
                               participant_hints, highlight_cards={('ai', target_idx)}, buttons=hint_buttons)
                    
                    hint_choice, hint_rt = wait_for_click_on_region(hint_buttons)
                    hint_type = "color" if hint_choice == "COLOR" else "position"
                    color, pos = computer_cards[target_idx]
                    hint_value = color if hint_type == "color" else pos
                    
                    total_rt = action_rt + card_rt + hint_rt
                    
                    # Log turn
                    turn_logs.append({
                        'turn': turn_count,
                        'player': 'Participant',
                        'action': 'Hint',
                        'details': f"Card {target_idx+1} {hint_type}: {hint_value}",
                        'rt': total_rt
                    })
                    
                    render_board(computer_cards, participant_cards, played_sequence,
                               f"You hinted: Card {target_idx+1} has {hint_value.upper()} ({hint_type})",
                               participant_hints, highlight_cards={('ai', target_idx)})
                    safe_wait(2.0)

                    # AI receives hint and decides what to do
                    can_play_slot = ai.receive_hint_from_participant(hint_type, hint_value, target_idx, (color, pos))
                    
                    if can_play_slot is not False and played_sequence[can_play_slot] is None:
                        # AI plays the card
                        played_sequence[can_play_slot] = (color, pos)
                        computer_cards[target_idx] = None
                        ai.play_card(target_idx, can_play_slot)
                        
                        # Log AI's immediate play
                        turn_logs.append({
                            'turn': turn_count,
                            'player': 'AI',
                            'action': 'Play',
                            'details': f"Slot {can_play_slot+1}: {color} {pos}",
                            'rt': None
                        })
                        
                        render_board(computer_cards, participant_cards, played_sequence,
                                   f"AI plays {color.upper()} {pos.upper()} in slot {can_play_slot+1}!",
                                   participant_hints)
                        safe_wait(2.5)
                        
                        ai.rounds_without_play = 0
                        
                        # Draw replacement
                        all_cards_in_use = computer_cards + participant_cards + [card for card in played_sequence if card]
                        new_card = draw_new_card(all_cards_in_use, missing_cards)
                        computer_cards[target_idx] = new_card
                    else:
                        render_board(computer_cards, participant_cards, played_sequence,
                                   "AI acknowledges the hint.",
                                   participant_hints)
                        safe_wait(2.0)

                elif action == "PLAY":
                    # Step 1: Select participant card
                    render_board(computer_cards, participant_cards, played_sequence,
                               "Click on YOUR card (bottom row) to play:", participant_hints)
                    
                    part_regions = {k: v for k, v in card_regions.items() if k[0] == 'participant'}
                    selected, card_rt = wait_for_click_on_region(part_regions)
                    card_idx = selected[1]
                    
                    if participant_cards[card_idx] is None:
                        render_board(computer_cards, participant_cards, played_sequence,
                                   "That slot is empty! Try again.", participant_hints)
                        safe_wait(1)
                        continue
                    
                    # Step 2: Select slot
                    slot_regions = {k: v for k, v in card_regions.items() if k[0] == 'slot'}
                    render_board(computer_cards, participant_cards, played_sequence,
                               f"Click a SLOT (middle row) to play card {card_idx+1}:",
                               participant_hints, highlight_cards={('participant', card_idx)})
                    
                    selected_slot, slot_rt = wait_for_click_on_region(slot_regions)
                    slot_idx = selected_slot[1]
                    
                    if played_sequence[slot_idx] is not None:
                        render_board(computer_cards, participant_cards, played_sequence,
                                   "That slot is taken! Try again.", participant_hints)
                        safe_wait(1)
                        continue
                    
                    total_rt = action_rt + card_rt + slot_rt
                    
                    played_card = participant_cards[card_idx]
                    played_sequence[slot_idx] = played_card
                    participant_cards[card_idx] = None
                    
                    # Clear hints for played card
                    participant_hints[card_idx] = {'color': None, 'position': None}
                    
                    # Log turn
                    turn_logs.append({
                        'turn': turn_count,
                        'player': 'Participant',
                        'action': 'Play',
                        'details': f"Card {card_idx+1} to Slot {slot_idx+1}",
                        'rt': total_rt
                    })
                    
                    ai.update_after_participant_action('play', card_played=played_card)
                    
                    render_board(computer_cards, participant_cards, played_sequence,
                               f"You played card {card_idx+1} to slot {slot_idx+1}!",
                               participant_hints)
                    safe_wait(1.5)
                    
                    # Draw replacement
                    all_cards_in_use = computer_cards + participant_cards + [card for card in played_sequence if card]
                    new_card = draw_new_card(all_cards_in_use, missing_cards)
                    participant_cards[card_idx] = new_card
                    # Reset hints for new card
                    participant_hints[card_idx] = {'color': None, 'position': None}

                elif action == "REPLACE":
                    # Select card to replace
                    render_board(computer_cards, participant_cards, played_sequence,
                               "Click on YOUR card (bottom row) to replace:", participant_hints)
                    
                    part_regions = {k: v for k, v in card_regions.items() if k[0] == 'participant'}
                    selected, card_rt = wait_for_click_on_region(part_regions)
                    replace_idx = selected[1]
                    
                    total_rt = action_rt + card_rt
                    
                    if participant_cards[replace_idx]:
                        old_card = participant_cards[replace_idx]
                        # Draw replacement
                        all_cards_in_use = computer_cards + participant_cards + [card for card in played_sequence if card]
                        new_card = draw_new_card(all_cards_in_use, missing_cards)
                        participant_cards[replace_idx] = new_card
                        
                        # Clear hints for replaced card
                        participant_hints[replace_idx] = {'color': None, 'position': None}
                        
                        # Log turn
                        turn_logs.append({
                            'turn': turn_count,
                            'player': 'Participant',
                            'action': 'Replace',
                            'details': f"Card {replace_idx+1}",
                            'rt': total_rt
                        })
                        
                        ai.participant_cards = participant_cards.copy()
                        
                        render_board(computer_cards, participant_cards, played_sequence,
                                   f"You replaced card {replace_idx+1}!",
                                   participant_hints)
                        safe_wait(1.5)

            else:
                # ===== AI TURN =====
                hint_strategy = ai.give_hint_to_participant()
                
                if hint_strategy:
                    hint_idx = hint_strategy['target_card']
                    hint_type = hint_strategy['hint_type']
                    hint_value = hint_strategy['hint_value']
                    
                    # Store hint in participant_hints
                    participant_hints[hint_idx][hint_type] = hint_value
                    
                    # Log turn
                    turn_logs.append({
                        'turn': turn_count,
                        'player': 'AI',
                        'action': 'Hint',
                        'details': f"Your card {hint_idx+1} {hint_type}: {hint_value}",
                        'rt': None
                    })
                    
                    msg = f"AI hints: Your card {hint_idx+1} has {hint_value.upper()} ({hint_type})"
                    if ai.rounds_without_play >= 2:
                        msg += f"\n[No cards played in {ai.rounds_without_play} rounds!]"
                    
                    render_board(computer_cards, participant_cards, played_sequence,
                               msg, participant_hints, highlight_cards={('participant', hint_idx)})
                    safe_wait(4.0)
                else:
                    # AI replaces a card
                    replace_idx = ai.choose_card_to_replace(computer_cards)
                    
                    if replace_idx is not None:
                        all_cards_in_use = computer_cards + participant_cards + [card for card in played_sequence if card]
                        new_card = draw_new_card(all_cards_in_use, missing_cards)
                        
                        old_card = computer_cards[replace_idx]
                        print(f"🤖 AI replacing card at position {replace_idx}: {old_card} with {new_card}")
                        
                        computer_cards[replace_idx] = new_card
                        
                        # Log turn
                        turn_logs.append({
                            'turn': turn_count,
                            'player': 'AI',
                            'action': 'Replace',
                            'details': f"Card {replace_idx+1}",
                            'rt': None
                        })
                        
                        render_board(computer_cards, participant_cards, played_sequence,
                                   f"AI replaced card {replace_idx+1}.",
                                   participant_hints)
                    else:
                        # Log waiting
                        turn_logs.append({
                            'turn': turn_count,
                            'player': 'AI',
                            'action': 'Wait',
                            'details': 'Waiting for more information',
                            'rt': None
                        })
                        
                        render_board(computer_cards, participant_cards, played_sequence,
                                   "AI is waiting for more information.",
                                   participant_hints)
                    
                    safe_wait(2.5)
                
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
        
        render_board(computer_cards, participant_cards, played_sequence,
                   f"Trial {trial_number} complete! {score_text}",
                   participant_hints)
        safe_wait(3.0)

        # Show comparison
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
        
        # Save turn log
        save_turn_log(player_name, trial_number, turn_logs)
        
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
        "• Click HINT - Give a hint about your partner's cards\n"
        "• Click PLAY - Play one of your cards\n"
        "• Click REPLACE - Replace one of your cards\n\n"
        "Your cards (bottom row) will show hints as colored squares and arrows!"
    )
    
    # Run two trials
    trial_results = []
    
    for trial_num in range(1, 3):
        if trial_num > 1:
            show_instructions_with_space(f"Ready for Trial {trial_num}?")
        
        trial_result = run_single_trial(trial_num, player_name)
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


# run_localizer()
run_practice()
# run_memory_game()

win.close()
core.quit()

