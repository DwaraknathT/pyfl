import abc

import torch
import torch.backends.cudnn as cudnn

from pyfl.communication.communicator import Communicator
from pyfl.communication.message import Message
from pyfl.communication.message_definitions import DeviceServerMessage, ServerDeviceMessage
from pyfl.communication.message_definitions import ServerDeviceSendClass, ServerDeviceNotifClass
from pyfl.utils import get_logger, get_model

logger = get_logger(__name__)
device2server = DeviceServerMessage()
server2device = ServerDeviceMessage()

if torch.cuda.is_available():
  device = 'cuda'
  cudnn.benchmark = True
else:
  device = 'cpu'


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
  * Server id: A unique identifier for the server
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

  def __init__(self, device_config, dataset, communicator):
    self.device_config = device_config
    self.dataset = dataset
    self.model = None
    self.optimizer = None
    self.communicator = communicator
    self.lr_scheduler = None
    self.participate = False
    self.task_config = None
    self.gradient_updates = []

  def build_device(self, task_config):
    self.model, self.optimizer = get_model(task_config)

  # def send_message(self,
  #                  message):
  #   logger.info('Sending Message {} to Server'.format(message.message_params))
  #   self.comm.send(message)
  #   server_response = self.recv_message()
  #   return server_response
  #
  # def recv_message(self):
  #   message = self.comm.recv()
  #   logger.info('Received Message {} from Server'.format(message.message_params))
  #   return message

  def apply_weights(self, weights_list):
    count = 0
    for layer in self.model.parameters():
      if hasattr(layer, 'mask'):
        layer.weight.data = weights_list[count]
        self.gradient_updates.append(torch.zeros_like(layer.weight.data))
        count += 1

  def ping_server(self):
    """
    Send the server a series of messages
    Messages sent:
    1. Tell the server device is ready to participate, see what the server says
    2. If accepted, ask the server for task config
    3. Ask the server for global model weights (build the model, optim objects based on task config)
    :return:
    """
    # participate_query_response = self.send_message(Message({
    #   'sender_id': self.device_config['device_id'],
    #   'receiver_id': self.device_config['server_id'],
    #   'message_class': device2server.D2S_NOTIF_CLASS,
    #   'message_type': device2server.D2S_NOTIF_CLASS.D2S_READY if
    #   self.device_config['ready']
    #   else device2server.D2S_NOTIF_CLASS.D2S_NOT_READY,
    #   'message': None
    # }))
    self.communicator.send_message(self.device_config['device_id'],
                                   self.device_config['server_id'],
                                   device2server.D2S_NOTIF_CLASS,
                                   device2server.D2S_NOTIF_CLASS.D2S_READY,
                                   None)
    exit(0)
    if not (isinstance(participate_query_response.message_class, ServerDeviceNotifClass)):
      logger.error('Wrong message class used by the server')
      raise ValueError
    else:
      self.participate = participate_query_response.message_type

    if self.participate == 0:
      return

    # Query the server for Task config, which is going to be a dict
    # with all training config params in it.
    task_query_response = self.send_message(Message({
      'sender_id': self.device_config['device_id'],
      'receiver_id': self.device_config['server_id'],
      'message_class': device2server.D2S_QUERY_CLASS,
      'message_type': device2server.D2S_QUERY_CLASS.D2S_QUERY_TASK_CONFIG,
      'message': None
    }))
    # Check if the received message of the correct class
    if not (isinstance(task_query_response.message_class, ServerDeviceSendClass)):
      logger.error('Wrong message class used by the server')
      raise ValueError
    else:
      # Store the task_config in the the class attribute
      self.task_config = task_query_response.message
      if self.task_config is None:
        logger.error('Task config is None type')

    # Create the model, optimizer object to store the global weights in it
    self.build_device(self.task_config)

    # Query the server for the global model weights
    model_query_response = self.send_message(Message({
      'sender_id': self.device_config['device_id'],
      'receiver_id': self.device_config['server_id'],
      'message_class': device2server.D2S_QUERY_CLASS,
      'message_type': device2server.D2S_QUERY_CLASS.D2S_QUERY_GLOBAL_MODEL,
      'message': None
    }))
    if not (isinstance(model_query_response['message_class'], ServerDeviceSendClass)):
      logger.error('Wrong message class used by the server')
      raise ValueError
    else:
      # Store the model in the the class attribute
      weights = task_query_response.message
      if self.model is None:
        logger.error('Model not instantiated')
      else:
        self.apply_weights(weights)
        logger.info('Applied global weights to local model')

  def store_grads(self):
    """
    Maintain a running average of the model's gradients to send to the server
    :return: None
    """
    count = 0
    for layer in self.model.parameters():
      if hasattr(layer, 'mask'):
        self.gradient_updates[count] = (0.7 * layer.weight.grad.data) + (0.3 * self.gradient_updates[count])
        count += 1

  def train_step(self):
    """
    Good ol' training step
    :return:
    """
    self.model.train()
    correct = 0
    for batch_idx, (data, target) in enumerate(self.dataset['trainset']):
      data, target = data.to(device), target.to(device)
      self.optimizer.zero_grad()
      output = self.model(data)
      loss = self.criterion(output, target)
      loss.backward()
      self.store_grads()
      self.optimizer.step()
      pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
      correct += pred.eq(target.view_as(pred)).sum().item()

  def execute_task(self):
    logger.info('Executing {} task'.format(self.task_config['task_name']))
    logger.info('Using task config {}'.format(self.task_config))

  def run_device(self):
    # Setting the device to ready
    self.device_config['ready'] = 1
    logger.info("Set device_config['ready'] to 1")
    # Ping the server to get task config and global weights to
    # start the task
    self.ping_server()
    exit(0)
    self.execute_task()

  def update_model(self):
    print('updating local model')
