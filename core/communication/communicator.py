from core.communication.message import Message
from core.communication.message_definitions import DeviceServerMessage, ServerDeviceMessage
from core.communication.message_definitions import DeviceServerSendClass, DeviceServerNotifClass, DeviceServerQueryClass
from core.communication.message_definitions import ServerDeviceSendClass, DeviceServerNotifClass, ServerDeviceQueryClass
import torch.multiprocessing as mp
from torch.multiprocessing import Process, Pipe, Value

class Channel:
  def __init__(self, sender_id, receiver_id, comm):
    self.sender_id = sender_id
    self.receiver_id = receiver_id
    self.comm = comm

class Communicator:
  def __init__(self):
    self.dev_serv_channels = {}
    self.serv_dev_channels = []

  def register(self, sender_id, receiver_id, comm):
    server_con, device_con = Pipe()
    dev_serv_channel = Channel(sender_id, receiver_id, device_con) #device is the sender (Device2Server)
    self.dev_serv_channels['sender_id'] = dev_serv_channel
    serv_dev_channel = Channel(receiver_id, sender_id, server_con)  #endB: Server is the sender
    self.serv_dev_channels['sender_id'] = serv_dev_channel

  def retrieve_comm(self,sender_id, receiver_id, msg_class):
    if hasattr(DeviceServerMessage, msg_class.toString()):  # sender_id : device_id &  recv_id : server_id
      return self.dev_serv_channels.get(sender_id).comm
    else:
      return self.serv_dev_channels.get(receiver_id).comm

  def send_message(self,sender_id, receiver_id, msg_class, msg_type, msg):
    message = Message({
      'sender_id': sender_id,
      'receiver_id': receiver_id,
      'message_class': msg_class,
      'message_type': msg_type,
      'message': msg
    })
    comm = self.retrieve_comm(sender_id, receiver_id, msg_class)

  def recv_message(self,sender_id, receiver_id):
    comm = self.retrieve_comm(sender_id, receiver_id, msg_class)

Let deivce_id be 1,2,..N , server id be S
We have (1,S, comm1s ), (2,S,comm2s) ... (n, S, commns)
(S,1,comms1), .... (s, n, commsn)

Device2server send  : search across first index .. comks
Server2device send : search across first index ->
