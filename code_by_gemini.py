from dobot_api import DobotDllType as dType
from warnings import warn
import math
import numpy as np

def main():
    api = dType.load()

    state = dType.ConnectDobot(api,"", 115200)[0]
    print("Connect status:", state)

    if not (state == dType.DobotConnect.DobotConnect_NoError):
        warn("Could not connect. Exiting...")
        exit()

    dType.SetQueuedCmdClear(api)

    # Async Motion Params Settings
    dType.SetHOMEParams(api, 200, 200, 100, 200, isQueued=1)
    dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, isQueued=1)
    dType.SetPTPCommonParams(api, 100, 100, isQueued=1)

    # --- Home at the start (as requested) ---
    # This ensures the robot is in a known state before starting operations.
    last_index_home_start = dType.SetHOMECmd(api, temp=0, isQueued=1)[0]
    dType.SetQueuedCmdStartExec(api)
    while last_index_home_start > dType.GetQueuedCmdCurrentIndex(api)[0]:
        dType.dSleep(100)
    dType.SetQueuedCmdStopExec(api) # Stop queue after homing is complete

    # Define coordinates and constants
    Z_SAFE = 0       # Safe Z-coordinate above blocks
    Z_PICK = -50     # Z-coordinate to pick up blocks (as per problem statement)
    R_HEAD = 0       # Rotation for the end effector (vacuum pump), typically 0
    PTP_MODE = dType.PTPMode.PTPMOVLXYZMode # Linear movement mode for precise paths

    # Estimated initial positions of the blocks based on the image and paper coordinates:
    # Paper top-left: (300, 100), bottom-right: (155, -100)
    # X decreases from "front" (left in image) to "back" (right in image)
    # Y decreases from "robot's left" (top in image) to "robot's right" (bottom in image)
    # The blocks are visually arranged horizontally near the top edge of the paper.

    # Initial positions (estimated based on visual inspection)
    x_green_initial = 270 # Green block is to the left-front (larger X)
    y_green_initial = 70  # Roughly along the top edge of the paper (larger Y)

    x_blue_initial = 225  # Blue block is in the middle X-wise
    y_blue_initial = 70   # Roughly along the top edge of the paper (larger Y)

    x_red_initial = 180   # Red block is to the right-back (smaller X)
    y_red_initial = 70    # Roughly along the top edge of the paper (larger Y)

    # Target X-coordinate for all blocks (same as blue block's initial X)
    # All blocks will be aligned along this X-coordinate.
    x_target_aligned = x_blue_initial # This is 225mm

    # Target Y-coordinates for the aligned row.
    # Spacing them out along the Y-axis to form a visible row.
    # Assuming blocks are approximately 25mm (1 inch) wide for adequate spacing.
    y_green_target_aligned = 25   # Green block positioned on one side of the Y-center
    y_blue_target_aligned = 0     # Blue block positioned at the Y-center of the row
    y_red_target_aligned = -25    # Red block positioned on the other side of the Y-center

    # List of block pick and place coordinates
    # We will pick them in order from green -> blue -> red
    blocks_to_move = [
        (x_green_initial, y_green_initial, x_target_aligned, y_green_target_aligned),
        (x_blue_initial, y_blue_initial, x_target_aligned, y_blue_target_aligned),
        (x_red_initial, y_red_initial, x_target_aligned, y_red_target_aligned),
    ]

    # Function to enable/disable vacuum pump (immediate command, not queued)
    def set_vacuum_pump(enable_pump):
        # suction_cup = 1, ctrl_mode = 1 are standard for vacuum pump
        dType.SetEndEffectorSuctionCup(api, 1, enable_pump, 1)
        dType.dSleep(500) # Short delay for the pump to actuate

    # Process each block for pick and place
    for i, (initial_x, initial_y, target_x, target_y) in enumerate(blocks_to_move):
        block_name = ["Green", "Blue", "Red"][i]
        print(f"Processing {block_name} block: from ({initial_x}, {initial_y}) to ({target_x}, {target_y})")

        # --- Movement sequence for picking up the block ---
        # 1. Move to a safe Z above the current block's initial X,Y position
        dType.SetQueuedCmdClear(api) # Clear queue to ensure only current commands are executed
        last_index = dType.SetPTPCmd(api, PTP_MODE, initial_x, initial_y, Z_SAFE, R_HEAD, isQueued=1)[0]
        dType.SetQueuedCmdStartExec(api)
        while last_index > dType.GetQueuedCmdCurrentIndex(api)[0]:
            dType.dSleep(100)
        dType.SetQueuedCmdStopExec(api)

        # 2. Lower the arm to the pick-up Z coordinate
        dType.SetQueuedCmdClear(api)
        last_index = dType.SetPTPCmd(api, PTP_MODE, initial_x, initial_y, Z_PICK, R_HEAD, isQueued=1)[0]
        dType.SetQueuedCmdStartExec(api)
        while last_index > dType.GetQueuedCmdCurrentIndex(api)[0]:
            dType.dSleep(100)
        dType.SetQueuedCmdStopExec(api)
        
        # 3. Turn on the vacuum pump to grip the block
        set_vacuum_pump(1) # This is an immediate command

        # 4. Raise the arm to the safe Z coordinate with the block
        dType.SetQueuedCmdClear(api)
        last_index = dType.SetPTPCmd(api, PTP_MODE, initial_x, initial_y, Z_SAFE, R_HEAD, isQueued=1)[0]
        dType.SetQueuedCmdStartExec(api)
        while last_index > dType.GetQueuedCmdCurrentIndex(api)[0]:
            dType.dSleep(100)
        dType.SetQueuedCmdStopExec(api)

        # --- Movement sequence for placing the block ---
        # 5. Move to a safe Z above the target X,Y position
        dType.SetQueuedCmdClear(api)
        last_index = dType.SetPTPCmd(api, PTP_MODE, target_x, target_y, Z_SAFE, R_HEAD, isQueued=1)[0]
        dType.SetQueuedCmdStartExec(api)
        while last_index > dType.GetQueuedCmdCurrentIndex(api)[0]:
            dType.dSleep(100)
        dType.SetQueuedCmdStopExec(api)

        # 6. Lower the arm to the place Z coordinate
        dType.SetQueuedCmdClear(api)
        last_index = dType.SetPTPCmd(api, PTP_MODE, target_x, target_y, Z_PICK, R_HEAD, isQueued=1)[0]
        dType.SetQueuedCmdStartExec(api)
        while last_index > dType.GetQueuedCmdCurrentIndex(api)[0]:
            dType.dSleep(100)
        dType.SetQueuedCmdStopExec(api)

        # 7. Turn off the vacuum pump to release the block
        set_vacuum_pump(0) # This is an immediate command

        # 8. Raise the arm to the safe Z coordinate after placing the block
        dType.SetQueuedCmdClear(api)
        last_index = dType.SetPTPCmd(api, PTP_MODE, target_x, target_y, Z_SAFE, R_HEAD, isQueued=1)[0]
        dType.SetQueuedCmdStartExec(api)
        while last_index > dType.GetQueuedCmdCurrentIndex(api)[0]:
            dType.dSleep(100)
        dType.SetQueuedCmdStopExec(api)

    # --- Final home command ---
    # Move the robot arm back to its home position after all operations are complete.
    dType.SetQueuedCmdClear(api)
    last_index_home_end = dType.SetHOMECmd(api, temp=0, isQueued=1)[0]
    dType.SetQueuedCmdStartExec(api)
    while last_index_home_end > dType.GetQueuedCmdCurrentIndex(api)[0]:
        dType.dSleep(100)
    dType.SetQueuedCmdStopExec(api)

    # Disconnect bot
    dType.DisconnectDobot(api)
    print("Dobot disconnected.")

if __name__ == "__main__":
    main()