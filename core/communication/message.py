from abc import ABC


class Message(ABC):
  def __init__(self, message_params):
    self.message_params = message_params
    self.sender_id = message_params['sender_id']
    self.receiver_id = message_params['receiver_id']
    self.message_class = message_params['message_class']
    self.message_type = message_params['message_type']
    self.message = message_params['message']

  def get_sender(self):
    return self.sender_id

  def get_receiver(self):
    return self.receiver_id

  def get_message_params(self):
    return self.message_params
