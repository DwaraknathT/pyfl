from abc import ABC


class DeviceBase(ABC):
  """
  Device abstract base class
  """

  def __init__(self, **kwargs):
    """
    Device initializer
    """
    raise NotImplementedError('Device base class not implemented')

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

  If the server accepts the participation request of the device,
  we set participate var to 1. If the request is rejected we set it to 0
  """

  def __init__(self, device_config, dataset):
    super(Device, self).__init__()
    self.device_config = device_config
    self.dataset = dataset
    self.model = None
    self.participate = False
    self.task_config = None
    self.updates = None

  def ping_server(self, server_config):
    if self.device_config['ready']:
      self.participate = send_message(server_config['server_id'], msg_class=0, msg_id=0)
    if self.participate:
      self.task_config = send_message(server_config['server_id'], msg_class=1, msg_id=1)
      self.model = send_message(server_config['server_id'], msg_class=1, msg_id=0)
      self.execute_task(self.task_config, model)
      if self.device_config['task_status'] == 1:
        self.update_model()
        self.device_config['sync_server'] = send_message('send grads')

  def update_model(self):
    print('updating local model')

  def execute_task(self, task_config, model):
    print('run training loop')
