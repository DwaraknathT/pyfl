from core.communication.message import Message
from core.communication.message_definitions import DeviceServerMessage, ServerDeviceMessage
from core.communication.message_definitions import DeviceServerSendClass, DeviceServerNotifClass, DeviceServerQueryClass
from core.communication.message_definitions import ServerDeviceSendClass, DeviceServerNotifClass, ServerDeviceQueryClass
import torch.multiprocessing as mp
import loguru
from collections import defaultdict
from torch.multiprocessing import Process, Pipe, Value
from core.utils import Attributes

log = loguru.logger
class Channel:
  def __init__(self, sender_id, receiver_id, comm):
    '''
    Creates the respective end of the communicative channel
    :param sender_id: Sender ID
    :param receiver_id: Receiver ID
    :param comm: Communicator object
    '''
    self.sender_id = sender_id
    self.receiver_id = receiver_id
    self.comm = comm

class Communicator:
  def __init__(self):
    self.__dev_serv_channels = {}
    self.__serv_dev_channels = defaultdict(list)

  def register(self, pointa_id, pointb_id):
    server_con, device_con = Pipe()
    dev_serv_channel = Channel(pointa_id, pointb_id, device_con) #endA: device is the sender
    self.__dev_serv_channels[pointa_id] = dev_serv_channel
    serv_dev_channel = Channel(pointb_id, pointa_id, server_con)  #endB: Server is the sender
    self.__serv_dev_channels[pointb_id].append(serv_dev_channel)
    log.debug("Registered dev_serv_channel {}".format(self.__dev_serv_channels.keys()))
    log.debug("Regostereed serv_dev_ channel {}".format(self.__serv_dev_channels.keys()))


  def __retrieve_comm_send(self, sender_id, receiver_id):
    return self.__dev_serv_channels.get(sender_id).comm

  def __retrieve_comm_recv(self, receiver_id):
    log.debug(self.__serv_dev_channels.keys())
    comms = []
    for channel in self.__serv_dev_channels.get(receiver_id):
      comms.append(channel.comm)
    return comms

  def send_message(self, sender_id, receiver_id, msg_class, msg_type, msg):
    message = Message({
      'sender_id': sender_id,
      'receiver_id': receiver_id,
      'message_class': msg_class,
      'message_type': msg_type,
      'message': msg
    })
    comm = self.__retrieve_comm_send(sender_id, receiver_id)
    comm.send(message)

  def recv_message(self, receiver_id):
    messages = []
    comms = self.__retrieve_comm_recv(receiver_id)
    for comm in comms:
      messages.append(comm.recv())
    return messages

device2server = DeviceServerMessage()
if __name__ == '__main__':
    comm = Communicator()
    comm.register(12, 34)
    comm.register(13, 34)
    comm.send_message(12, 34, device2server.D2S_QUERY_CLASS, device2server.D2S_QUERY_CLASS.D2S_QUERY_TASK_CONFIG, None)
    comm.send_message(13, 34, device2server.D2S_QUERY_CLASS, device2server.D2S_QUERY_CLASS.D2S_QUERY_TASK_CONFIG, None)
    messages = comm.recv_message(34)
    #message2 = comm.recv_message(13,34)
    print(messages)
    #print(message2.message_class)
