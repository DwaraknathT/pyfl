import loguru
from torch.multiprocessing import Pipe

from pyfl.communication.message import Message

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
    self.__channels = {}

  def register(self, pointa_id, pointb_id):
    server_con, device_con = Pipe()
    self.__channels[(pointa_id, pointb_id)] = Channel(pointa_id, pointb_id, device_con)  # endA: device is the sender
    self.__channels[(pointb_id, pointa_id)] = Channel(pointb_id, pointa_id, server_con)  # endB: Server is the sender
    log.debug("Registered channel {}".format(self.__channels.keys()))

  def is_registered(self, pointa_id, pointb_id):
    return ((pointa_id, pointb_id) in self.__channels)

  def __retrieve_comm_send(self, sender_id, receiver_id):
    return self.__channels.get((sender_id, receiver_id)).comm

  def __retrieve_comm_recv(self, receiver_id):
    log.debug(self.__channels.keys())
    comms = []
    for key in self.__channels.keys():
      if receiver_id == key[0]:
        comms.append(self.__channels[key].comm)
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
      if comm.poll(0.001):
        messages.append(comm.recv())
    return messages
