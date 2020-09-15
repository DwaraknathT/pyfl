import pytest
from pyfl.communication.communicator import Communicator
from pyfl.communication.message import Message
from pyfl.communication.message_definitions import DeviceServerMessage, ServerDeviceMessage

device2server = DeviceServerMessage()
server2device = ServerDeviceMessage()

@pytest.mark.communicator
def test_communicator():
  comm = Communicator()
  '''
  Register four devices with device_id's 1,2,3,4 respectively
  Register a server with server_id 34
  Tests send_message and recv_message for the following:
  - Multiple Devices ->Server  
  - Server -> Multiple devices  
  '''
  comm.register(1, 34)
  comm.register(2, 34)
  comm.register(3, 34)
  comm.register(4, 34)
  assert comm.is_registered(3, 34), "Registration failed - (3,34)"
  comm.send_message(1, 34, device2server.D2S_QUERY_CLASS, device2server.D2S_QUERY_CLASS.D2S_QUERY_TASK_CONFIG, None)
  comm.send_message(2, 34, device2server.D2S_QUERY_CLASS, device2server.D2S_QUERY_CLASS.D2S_QUERY_TASK_CONFIG, None)
  messages = comm.recv_message(34)
  # assert len(messages) == 2, "Receive Messages failed"
  # comm.send_message(34, 2, server2device.S2D_NOTIF_CLASS, server2device.S2D_NOTIF_CLASS.S2D_SELECTED, None)
  # comm.send_message(34, 3, server2device.S2D_SEND_CLASS, server2device.S2D_SEND_CLASS.S2D_SEND_GLOBAL_MODEL, None)
  # msg1 = comm.recv_message(2)
  # msg2 = comm.recv_message(3)
  # assert (len(msg1) is not 0) and (len(msg2) is not 0), "Device receive message failed"