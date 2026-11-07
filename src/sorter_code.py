#!/usr/bin/env python3
"""
ev3dev2 translation of an EV3-G program:

  Loop (6 times):
      Read color sensor
      Switch on color (Blue / Green / Red / Yellow):
          - Play a sound for that color
          - Drive large motors A+D (tank) a set distance, steering one way
          - Stop A+D
          - Rotate medium motor B 360 degrees at speed 50
          - Drive large motors A+D back the same distance, steering the other way
          - Stop A+D

Only the "distance" (degrees) value differs between the four cases:
  Blue = 1000, Green = 800, Red = 600, Yellow = 400
Adjust SETTINGS below to match your exact block values if they differ.
"""

from ev3dev2.motor import (
    MoveTank,
    MediumMotor,
    OUTPUT_A,
    OUTPUT_B,
    OUTPUT_D,
    SpeedPercent,
)
from ev3dev2.sensor import INPUT_1
from ev3dev2.sensor.lego import ColorSensor
from ev3dev2.sound import Sound

# ---------------------------------------------------------------------------
# Device setup
# ---------------------------------------------------------------------------
tank = MoveTank(OUTPUT_A, OUTPUT_D)     # large drive motors on A and D
arm = MediumMotor(OUTPUT_B)             # light/medium motor on B
color_sensor = ColorSensor(INPUT_1)     # plug color sensor into port 1
sound = Sound()

color_sensor.mode = ColorSensor.MODE_COL_COLOR

# ---------------------------------------------------------------------------
# Map raw sensor color values to friendly names used in the switch cases
# ---------------------------------------------------------------------------
COLOR_NAMES = {
    ColorSensor.COLOR_BLUE: "Blue",
    ColorSensor.COLOR_GREEN: "Green",
    ColorSensor.COLOR_RED: "Red",
    ColorSensor.COLOR_YELLOW: "Yellow",
}

# Per-color parameters, taken from the values shown in each switch case block
# steering: -20/20 (left) then reversed 20/-20 (right) on the way back
# degrees:  how far the B+C tank move runs in each direction
SETTINGS = {
    "Blue":   {"degrees": 1000},
    "Green":  {"degrees": 800},
    "Red":    {"degrees": 600},
    "Yellow": {"degrees": 400},
}

STEERING = 20      # matches the -20 / 20 values in the motor blocks
ARM_SPEED = 50     # motor A speed
ARM_DEGREES = 360  # motor A rotation amount
LOOP_COUNT = 6      # outer loop counter shown in the diagram


def run_case(color_name, degrees):
    """Runs the sequence of blocks found inside one switch case."""

    # 1. Play a sound announcing/identifying the color
    sound.speak(color_name)
    # If your program instead plays a specific sound FILE per color, use:
    # sound.play_file('/home/robot/sounds/%s.wav' % color_name.lower(), volume=100)

    # 2. Drive motors A+D forward, steering left, for the case's distance
    tank.on_for_degrees(
        SpeedPercent(-STEERING),
        SpeedPercent(STEERING),
        degrees,
        brake=True,
        block=True,
    )
    tank.off()

    # 3. Rotate medium motor B one full turn
    arm.on_for_degrees(SpeedPercent(ARM_SPEED), ARM_DEGREES, brake=True, block=True)

    # 4. Drive motors A+D back, steering reversed, same distance
    tank.on_for_degrees(
        SpeedPercent(STEERING),
        SpeedPercent(-STEERING),
        degrees,
        brake=True,
        block=True,
    )
    tank.off()


def main():
    for _ in range(LOOP_COUNT):
        detected = color_sensor.color
        color_name = COLOR_NAMES.get(detected)

        if color_name is None:
            # No matching case (sensor saw white/black/no color) -> skip, like
            # the switch block falling through with nothing to run
            continue

        settings = SETTINGS[color_name]
        run_case(color_name, settings["degrees"])


if __name__ == "__main__":
    main()
