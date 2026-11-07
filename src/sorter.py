#!/usr/bin/env python3

from ev3dev2.motor import MoveTank, MediumMotor
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_D
from ev3dev2.motor import SpeedPercent

from ev3dev2.sensor import INPUT_3
from ev3dev2.sensor.lego import ColorSensor

from ev3dev2.sound import Sound

import time


# =========================================================
# ROBOT CONFIGURATION
# =========================================================

# Motors A and D control the robot's movement.
tank_drive = MoveTank(OUTPUT_A, OUTPUT_D)

# Motor B operates the block-sorting mechanism.
sort_motor = MediumMotor(OUTPUT_B)

# Colour sensor connected to input port S3.
color_sensor = ColorSensor(INPUT_3)

# EV3 speaker for audio feedback.
sound = Sound()


# =========================================================
# MOVEMENT AND MOTOR SETTINGS
# =========================================================

DRIVE_SPEED = 25
STOPPER_SPEED = 20


# =========================================================
# DISTANCE CONFIGURATION
# =========================================================

# Reference measurement:
# Approximately 3 motor rotations correspond to 15 cm.
MOTOR_ROTATIONS_15CM = 3.0

# Distance assigned to each colour.
# These values represent motor rotations.
COLOR_TO_ROTATIONS = {
    "Red": 2.0,
    "Yellow": 4.0,
    "Green": 6.0
}


# =========================================================
# SORTING MECHANISM POSITIONS
# =========================================================

# Preset positions of the medium motor.
STOPPER_SCAN_POSITION = 0
STOPPER_HOLD_POSITION = 45
STOPPER_RELEASE_POSITION = 180

# Additional movement intended to help clear stuck blocks.
STOPPER_CLEAR_POSITION = 100

# Delays used during the block-release process.
RELEASE_WAIT = 0.5
CLEAR_WAIT = 0.5


# =========================================================
# BLOCK COUNT
# =========================================================

# Total number of blocks to be sorted in one run.
TOTAL_BLOCKS = 5


# =========================================================
# SORTING MOTOR CONTROL
# =========================================================

def move_stopper(position):
    """Move the sorting mechanism to a specified position."""

    print("Moving stopper to:", position)

    sort_motor.on_to_position(
        SpeedPercent(STOPPER_SPEED),
        position
    )

    time.sleep(0.3)


def hold_block():
    """Move the stopper into position to hold the block."""

    print("Holding block...")
    move_stopper(STOPPER_HOLD_POSITION)


def prepare_for_scan():
    """Move the stopper to its scanning position."""

    print("Preparing for colour scan...")

    move_stopper(STOPPER_SCAN_POSITION)

    time.sleep(0.3)


# =========================================================
# COLOUR DETECTION
# =========================================================

def detect_color():
    """
    Read the colour sensor three times.

    A colour is accepted only when all three readings
    consistently identify the same supported colour.
    """

    print("Scanning colour...")

    readings = []

    # Collect three sensor readings.
    for i in range(3):

        color = color_sensor.color_name

        print("Reading", i + 1, ":", color)

        if color == "Red":
            readings.append("Red")

        elif color == "Yellow":
            readings.append("Yellow")

        elif color == "Green":
            readings.append("Green")

        else:
            readings.append("Unknown")

        time.sleep(0.2)

    # Confirm that all three readings match.
    if readings[0] == readings[1] and readings[1] == readings[2]:

        if readings[0] == "Red":
            print("Confirmed: RED")
            sound.beep()
            return "Red"

        elif readings[0] == "Yellow":
            print("Confirmed: YELLOW")
            sound.beep()
            return "Yellow"

        elif readings[0] == "Green":
            print("Confirmed: GREEN")
            sound.beep()
            return "Green"

    # Return None if the readings are inconsistent
    # or the colour is not supported.
    print("Colour not confirmed.")

    return None


# =========================================================
# BLOCK RELEASE MECHANISM
# =========================================================

def release_block():
    """Release the block and perform an additional clearing movement."""

    print("Releasing block...")

    # Step 1: Move the stopper to the release position.
    move_stopper(STOPPER_RELEASE_POSITION)

    time.sleep(RELEASE_WAIT)

    # Step 2: Perform an additional movement to help
    # clear a block that may be stuck in the mechanism.
    print("Clearing block...")

    move_stopper(STOPPER_CLEAR_POSITION)

    time.sleep(CLEAR_WAIT)

    # Step 3: Return the stopper to its holding position.
    print("Returning stopper to hold position...")

    move_stopper(STOPPER_HOLD_POSITION)

    time.sleep(0.3)


# =========================================================
# ROBOT MOVEMENT
# =========================================================

def drive_forward(rotations):
    """Move the robot forward for the specified rotations."""

    print("Moving forward:", rotations, "rotations")

    tank_drive.on_for_rotations(
        SpeedPercent(DRIVE_SPEED),
        SpeedPercent(-DRIVE_SPEED),
        rotations
    )

    tank_drive.off()

    time.sleep(0.3)


def drive_backward(rotations):
    """
    Reverse the same number of rotations to return
    the robot to its starting position.
    """

    print("Returning to START:", rotations, "rotations")

    tank_drive.on_for_rotations(
        SpeedPercent(-DRIVE_SPEED),
        SpeedPercent(DRIVE_SPEED),
        rotations
    )

    tank_drive.off()

    time.sleep(0.3)


# =========================================================
# PROGRAM INITIALIZATION
# =========================================================

print("")
print("--------------------------------")
print("EV3 COLOR SORTING ROBOT")
print("--------------------------------")

print("Number of blocks:", TOTAL_BLOCKS)
print("")

# Set the sorting mechanism to its holding position
# before starting the sorting process.
hold_block()

time.sleep(1)


# =========================================================
# MAIN SORTING LOOP
# =========================================================

sorted_blocks = 0

# Continue until all five blocks have been processed.
while sorted_blocks < TOTAL_BLOCKS:

    print("")
    print("--------------------------------")
    print("BLOCK", sorted_blocks + 1)
    print("--------------------------------")

    # Step 1: Prepare the colour sensor for scanning.
    prepare_for_scan()

    # Step 2: Identify the colour of the current block.
    color = detect_color()

    # Step 3: Retry the same block if its colour
    # could not be confirmed.
    if color is None:

        print("Colour not detected.")
        print("Trying the same block again...")

        hold_block()

        time.sleep(1)

        continue

    # Step 4: Secure the block before moving.
    hold_block()

    # Step 5: Get the movement distance assigned
    # to the detected colour.
    rotations = COLOR_TO_ROTATIONS[color]

    print("")
    print("Detected colour:", color)
    print("Required rotations:", rotations)

    # Step 6: Move forward to the corresponding
    # colour-sorting location.
    drive_forward(rotations)

    # Step 7: Release the block at its destination.
    release_block()

    # Step 8: Reverse the same number of rotations
    # to return to the starting position.
    drive_backward(rotations)

    print("")
    print("Returned to START.")

    # Step 9: Update the count after completing
    # the sorting and return sequence.
    sorted_blocks = sorted_blocks + 1

    print(
        "Blocks sorted:",
        sorted_blocks,
        "/",
        TOTAL_BLOCKS
    )

    time.sleep(1)


# =========================================================
# PROGRAM COMPLETION
# =========================================================

# Stop the drive motors after all blocks are processed.
tank_drive.off()

print("")
print("--------------------------------")
print("ALL 5 BLOCKS SORTED")
print("--------------------------------")

sound.beep()

time.sleep(1)
