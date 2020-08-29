import abc

from core.communication.message import Message
from core.communication.message_definitions import DeviceServerMessage, ServerDeviceMessage
from core.utils import get_logger, get_model

logger = get_logger(__name__)
device2server = DeviceServerMessage()
server2device = ServerDeviceMessage()


class DeviceBase(object):
  """
  Device abstract base class
  """
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def __init__(self, **kwargs):
    """
    Device initializer
    """
    raise NotImplementedError('Device base class not implemented')

  def build_device(self, **kwargs):
    """
    Build device object based on given arguments 
    """
    raise NotImplementedError('Build device not implemented')

  def run_device(self, **kwargs):
    """
    Start the device
    """
    raise NotImplementedError('Run device not implemented')

  def ping_server(self, **kwargs):
    """
    Ping the server when the device is ready
    """
    raise NotImplementedError('Device-Server class not implemented')

  def execute_task(self, **kwargs):
    """
    Execute the give tak given by the server and store the updates
    """
    raise NotImplementedError('Executes one round of')

  def update_model(self, **kwargs):
    """
    Send the updates to the server as well as updated the base model
    """
    raise NotImplementedError('Model update not implemented')


class Device(DeviceBase):
  """
  Device class

  What is Device config ? A dict with the following params:
  * Device id : A unique identifier for each device
  * Ready : Is the device ready to participate
    0 : Ready to participate
    1 : Not ready to participate
  * Participate : Does the device train or not (based on server's response)
    1 : Server gave clearance to participate
    0 : Server rejected participation request
  * Task_status : Status of the task at hand
    0 : Task running
    1 : Task finished
    -1 : Task aborted
  * Update_local_model : Has it updated the local model ?
    0 - Not updated
    1 - updated
  * Sync_server : Send the gradient updates to server
    0 : The updates are not sent
    1 : The updates are sent

  Device2Server message system:
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

  If the server accepts the participation request of the device,
  we set participate var to 1. If the request is rejected we set it to 0
  """

  def __init__(self, device_config, comm, dataset):
    self.device_config = device_config
    self.dataset = dataset
    self.model = None
    self.optim = None
    self.comm = comm
    self.lr_scheduler = None
    self.participate = False
    self.task_config = None
    self.updates = None

  def build_device(self, task_config):
    self.model, self.optim = get_model(task_config)

  def run_device(self):
    # Setting the device to ready
    self.device_config['ready'] = 1
    logger.info("Set device_config['ready'] to 1")
    self.ping_server()

  def send_message(self,
                   message):
    logger.info('Sending Message {} to Server'.format(message))
    self.comm.send(message)
    self.receive()
    return 0

  def ping_server(self):
    self.participate = self.send_message(Message({
      'sender_id': self.device_config['device_id'],
      'receiver_id': self.device_config['server_id'],
      'message_class': device2server.D2S_NOTIF_CLASS,
      'message_type': device2server.D2S_NOTIF_CLASS.D2S_READY if
      self.device_config['ready']
      else device2server.D2S_NOTIF_CLASS.D2S_NOT_READY,
      'message': None
    }))

    if self.participate:
      self.task_config = self.send_message(Message({
        'sender_id': self.device_config['device_id'],
        'receiver_id': self.device_config['server_id'],
        'message_class': device2server.D2S_NOTIF_CLASS,
        'message_type': device2server.D2S_NOTIF_CLASS.D2S_READY if
        self.device_config['ready']
        else device2server.D2S_NOTIF_CLASS.D2S_NOT_READY,
        'message': None
      }))

      self.model = self.send_message(Message({
        'sender_id': self.device_config['device_id'],
        'receiver_id': self.device_config['server_id'],
        'message_class': device2server.D2S_NOTIF_CLASS,
        'message_type': device2server.D2S_NOTIF_CLASS.D2S_READY if
        self.device_config['ready']
        else device2server.D2S_NOTIF_CLASS.D2S_NOT_READY,
        'message': None
      }))

      self.execute_task(self.task_config, model)
      if self.device_config['task_status'] == 1:
        self.update_model()
        self.device_config['sync_server'] = self.send_message(Message(
          {'sender_id': self.device_config['device_id'],
           'receiver_id': self.device_config['server_id'],
           'message_class': device2server.D2S_NOTIF_CLASS,
           'message_type': device2server.D2S_NOTIF_CLASS.D2S_READY if
           self.device_config['ready']
           else device2server.D2S_NOTIF_CLASS.D2S_NOT_READY,
           'message': None}))

  def update_model(self):
    print('updating local model')

  def execute_task(self, task_config, model):
    print('run training loop')
