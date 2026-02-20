"""----------------------------------------------------
Turn the vacuum pump off when Gemini fails to do so.
----------------------------------------------------"""
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

    # Turn suction off
    #   To turn on instead, change the third parameter to 1
    dType.SetEndEffectorSuctionCup(api, 1, 0, 1)    # api, enableCtrl, on/off, isQueued

    # Start executing Command Queue
    dType.SetQueuedCmdStartExec(api)

    # Stop executing Command Queue
    dType.SetQueuedCmdStopExec(api)

    # Disconnect bot
    dType.DisconnectDobot(api)


if __name__ == "__main__":
    main()
