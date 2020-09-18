"""
Message interfaces between various actors
"""
import inspect
import types


class DeviceServerNotifClass(object):
  """
  0 : Not Ready for participation
  1 : Ready for participation
  2 : Task running
  3 : Task finished
  -1 : Task aborted
  """
  D2S_NOT_READY = 0
  D2S_READY = 1
  D2S_TASK_RUNNING = 2
  D2S_TASK_FINISHED = 3
  D2S_TASK_ABORTED = -1


class DeviceServerQueryClass(object):
  """
  0: Ask for the global model
  1: Ask for task configuration file
  """
  D2S_QUERY_GLOBAL_MODEL = 0
  D2S_QUERY_TASK_CONFIG = 1


class DeviceServerSendClass(object):
  """
  0 : Send the gradient updates
  1 : Send the task metrics
  """
  D2S_SEND_GRADIENT_UPDATES = 0
  D2S_SEND_TASK_METRICS = 1


class ServerDeviceNotifClass(object):
  """
  1 : Notify the device it's selected
  0 : Notify the device to try later
  """
  S2D_SELECTED = 1
  S2D_TRY_LATER = 0


class ServerDeviceQueryClass(object):
  """
  0 : Query the device if it's alive
  1 : Query the device if it's ready
  """
  S2D_CHECK_ALIVE_STATUS = 0
  S2D_CHECK_READY_STATUS = 1


class ServerDeviceSendClass(object):
  """
  0 : Send the global model
  1 : Send the task config
  2 : Send the task metrics
  """
  S2D_SEND_GLOBAL_MODEL = 0
  S2D_SEND_TASK_CONFIG = 1
  S2D_SEND_TASK_METRICS = 2


class ServerDeviceMessage(object):
  """
  Server2Device message system:
  Message Class : what it does
  0 : Class of Notification messages from server to device
    0 : Notify the device it's selected
    1 : Notify the device to try later
  1 : Class of Query messages from server to device
    0 : Query the device if it's alive
    1 : Query the device if it's ready
  2 : Send the device some stuff
    0 : Send the global model
    1 : Send the task config
    2 : Send the task metrics
  """
  S2D_NOTIF_CLASS = ServerDeviceNotifClass()
  S2D_QUERY_CLASS = ServerDeviceQueryClass()
  S2D_SEND_CLASS = ServerDeviceSendClass()


class DeviceServerMessage(object):
  """
  Device-Server message system:
  We have three classes of messages
  Message Class : what it does
  0 : Class of notification messages from device to server
    0 : Not Ready for participation
    1 : Ready for participation
    2 : Task running
    3 : Task finished
    -1 : Task aborted
  1 : Ask the server for model or task scheme
    0: Ask for the global model
    1: Ask for task configuration file
  2 : Send the server some stuff
    0 : Send the gradient updates
    1 : Send the task metrics
  """
  D2S_NOTIF_CLASS = DeviceServerNotifClass()
  D2S_QUERY_CLASS = DeviceServerQueryClass()
  D2S_UPDATE_CLASS = DeviceServerSendClass()
