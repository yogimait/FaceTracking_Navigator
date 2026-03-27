# gestures/click_config.py

import config

# Distance in normalized landmark space to consider a pinch active.
PINCH_THRESHOLD = getattr(config, 'CLICK_THRESHOLD', 0.04)

# Consecutive frames needed before a pinch is considered stable.
DEBOUNCE_FRAMES = 1

# Click zone stability gating (index fingertip movement based).
STABILITY_FRAMES = 2
MOVE_THRESHOLD = 0.02

# Activation delays for click actions.
LEFT_CLICK_ACTIVATION_TIME = 0.0
RIGHT_CLICK_ACTIVATION_TIME = 0.0

# Optional hold-based double click using thumb-index pinch.
DOUBLE_CLICK_ENABLED = True
DOUBLE_CLICK_HOLD = 0.75

# Cooldown after any click action.
GLOBAL_COOLDOWN = 0.25

# On-screen feedback label duration.
FEEDBACK_DURATION = 0.45
