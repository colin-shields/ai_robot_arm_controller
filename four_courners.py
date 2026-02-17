"""
This file controls the Dobot. Most of it is based on the DobotControl.py demo file.
"""
from dobot_api import DobotDllType as dType     # I had to change the original name of the library because it had hyphens in it
from warnings import warn
import math
import numpy as np      # pip install numpy


def check_coords(x, y, z=0) -> tuple[int, int, int]:
    """
    Checks whether the given coordinates are in-bounds (i.e., if they will cause a collision if executed).
    :param x:   front-back
    :param y:   left-right
    :param z:   up-down
    :return:    original coords if safe; coords adjusted to be on boundary if not
    """
    dist_from_center = math.sqrt(x**2 + y**2)
    if (not 200 <= dist_from_center <= 320) or (x < 0):
        warn(f"x:{x} y:{y} z:{z} coordinates cause collision")
        angle = -math.atan(y/x)
        new_x = 200 * math.cos(angle) if dist_from_center <= 200 else 320 * math.cos(angle)
        new_y = -200 * math.sin(angle) if dist_from_center <= 200 else -320 * math.sin(angle)
        return int(new_x), int(new_y), int(z)
    return int(x), int(y), int(z)


def polar_to_rect(r, theta1, theta2=0, in_degrees=False) -> tuple[int, int, int]:
    """
    Converts polar coordinates to rectangular coordinates.
    :param r:       distance from 0, 0, 0 (center of bot?) to arm
    :param theta1:  angle in xy-plane from y=0
    :param theta2:  angle above xy-plane
    :param in_degrees:  if True, assumes angle given is in degrees
    :return:
    """
    if in_degrees:
        theta1 *= math.pi / 180
        theta2 *= math.pi / 180
    x = r * math.cos(theta1) * math.cos(theta2)
    y = -r * math.sin(theta1) * math.cos(theta2)
    z = r * math.sin(theta2)
    return int(x), int(y), int(z)


def interpolate_polar(p1: tuple, p2: tuple, step=20) -> list[tuple]:
    """
    Move from one polar point to another in a smooth arc (as to not hit the robot with itself)
    :param p1:      (r, theta1, theta2)
    :param p2:      (r, theta1, theta2)
    :param step:    number of intermediate values
    :return:
    """
    a = np.linspace(p1[0], p2[0], step)
    b = np.linspace(p1[1], p2[1], step)
    c = np.linspace(p1[2], p2[2], step)

    return_list = []
    for i in range(20):
        return_list.append((float(a[i]), float(b[i]), float(c[i])))
    return return_list


def cc(x, y, z=0):
    """Short call name for check_coords()"""
    return check_coords(x, y, z)


def p2r(r, theta1, theta2=0, in_degrees=True):
    """Short call name for polar_to_rectangular()"""
    return polar_to_rect(r, theta1, theta2, in_degrees)


def p2r2(r, theta1, theta2=0, in_degrees=True):
    """Shortcut for calling check_coords(*polar_to_rect())"""
    return check_coords(*polar_to_rect(r, theta1, theta2, in_degrees))


# not yet implemented correctly. use main() instead.
def run_bot(*cmds, home=True):
    """

    :param cmds: Commands to run
    :param home: If True, homes the bot; default is True
    :return:
    """
    api = dType.load()

    state = dType.ConnectDobot(api, "", 115200)[0]
    print("Connect status:", state)

    if not (state == dType.DobotConnect.DobotConnect_NoError):
        warn("Could not connect. Exiting...")
        exit()

    # Async Motion Params Settings
    dType.SetHOMEParams(api, 200, 200, 200, 200, isQueued=1)
    dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, isQueued=1)
    dType.SetPTPCommonParams(api, 100, 100, isQueued=1)

    # Asynch Home
    #   NOTE: only home once after bot reset (for SOME reason??) actually wait maybe not?? idk ._.
    if home:
        dType.SetHOMECmd(api, temp=0, isQueued=1)

    # Async PTP Motion
    #   X-axis --> front to back (I'm calling the side with the cable ports the back)
    #   Y-axis --> side to side
    #   Z-axis --> up & down
    indexes = list[cmds]
    last_index = indexes[-1]

    # Start executing Command Queue
    dType.SetQueuedCmdStartExec(api)

    # Wait for executing last command
    while last_index > dType.GetQueuedCmdCurrentIndex(api)[0]:
        dType.dSleep(1000)

    # Stop executing Command Queue
    dType.SetQueuedCmdStopExec(api)

    # Disconnect bot
    dType.DisconnectDobot(api)


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

    # Asynch Home
    #   NOTE: only home once after bot reset (for SOME reason??) actually wait maybe not?? idk ._.
    dType.SetHOMECmd(api, temp=0, isQueued=1)

    # Async PTP Motion
    #   X-axis --> front to back (I'm calling the side with the cable ports the back)
    #   Y-axis --> side to side
    #   Z-axis --> up & down

    indexes = [# Sweep
               # dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, *p2r2(250, 45, -15, True), rHead=50, isQueued=1)[0],
               # dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, *p2r2(250, -45, 15, True), rHead=50, isQueued=1)[0],
               # Square
               # dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, *cc(260, 100, 0), rHead=50, isQueued=1)[0],
               # dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, *cc(220, 100, 0), rHead=50, isQueued=1)[0],
               # dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, *cc(220, 140, 0), rHead=50, isQueued=1)[0],
               # dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, *cc(260, 140, 0), rHead=50, isQueued=1)[0],
               # dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, *cc(260, 100, 0), rHead=50, isQueued=1)[0],
               # dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, *cc(125, 100, -20), rHead=50, isQueued=1)[0],
               # dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, *cc(125, -50, -20), rHead=50, isQueued=1)[0],
               # dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, *cc(300, -50, -20), rHead=50, isQueued=1)[0],
               # dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, *cc(300, 100, -20), rHead=50, isQueued=1)[0],
               # dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, *cc(150, 0, -20), rHead=50, isQueued=1)[0],

               dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 155, 0, -50, rHead=50, isQueued=1)[0],
               dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 300, 0, -50, rHead=50, isQueued=1)[0],
               dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 155, -100, -50, rHead=50, isQueued=1)[0],
               dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 155, 100, -50, rHead=50, isQueued=1)[0],
               dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 300, -100, -50, rHead=50, isQueued=1)[0],
               dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 300, 100, -50, rHead=50, isQueued=1)[0],

               # dType.SetEndEffectorSuctionCup(api, 1, 1, 1) # suction_cup=1, enable_pump=1 (on), ctrl_mode=1 (blocking/synchronous)

               # dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 227.5, 0.0, -50, rHead=50)[0],
               # dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, *cc(150, 0, -20), rHead=50, isQueued=1)[0],
               ]
    last_index = indexes[-1]

    # Start executing Command Queue
    dType.SetQueuedCmdStartExec(api)

    # Wait for executing last command
    while last_index > dType.GetQueuedCmdCurrentIndex(api)[0]:
        dType.dSleep(1000)

    # Stop executing Command Queue
    dType.SetQueuedCmdStopExec(api)

    # Disconnect bot
    dType.DisconnectDobot(api)


if __name__ == "__main__":
    pass
    # for point in interpolate_polar((100, 0, 0), (200, -90, 0)):
    #     print(p2r(*point)[:-1])
    # print(p2r2(260, -15))
    # run_bot()
    main()
