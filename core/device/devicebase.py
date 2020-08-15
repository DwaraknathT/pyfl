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
