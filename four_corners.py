"""----------------------------------------------------------------------------------------
This file moves the robot's head to the center line and four corners of the working area
----------------------------------------------------------------------------------------"""
from dobot_api import DobotDllType as dType
from warnings import warn


def main():
    api = dType.load()

    state = dType.ConnectDobot(api, "", 115200)[0]
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
    #   NOTE: if the bot has just been reset, it will not run this (for some reason???)
    dType.SetHOMECmd(api, temp=0, isQueued=1)

    # Async PTP Motion Axes
    #   X-axis --> front to back (I'm calling the side with the cable ports the back)
    #   Y-axis --> side to side
    #   Z-axis --> up & down

    # Move to the centerline & corners of the workspace.
    indexes = [dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 155, 0, -50, rHead=50, isQueued=1)[0],
               dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 300, 0, -50, rHead=50, isQueued=1)[0],
               dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 155, -100, -50, rHead=50, isQueued=1)[0],
               dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 155, 100, -50, rHead=50, isQueued=1)[0],
               dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 300, -100, -50, rHead=50, isQueued=1)[0],
               dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 300, 100, -50, rHead=50, isQueued=1)[0],
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
    main()
