from abc import ABC
from core.utils import get_logger

logger = get_logger(__name__)


class SelectorBase(ABC):
  """
  Selector abstract base class
  """

  def __init__(self, **kwargs):
    """
    Initialize the selector
    """
    raise NotImplementedError('Selector initializer not implemented')

  # def ping_coordinator(self, **kwargs):
  #   """
  #   Ping the coordinator to get the task info and number of devices,
  #   required.
  #   """
  #   raise NotImplementedError('Coordinator selector interface not implemented')

  def ping_devices(self, **kwargs):
    """
    Get signal from all devices which are available
    """
    raise NotImplementedError('Selector-device interface not implemented')

  def select_devices(self, **kwargs):
    """
    Select devices based on a set of criteria, and register them.
    Send the registered device list to coordinator.
    """
    raise NotImplementedError('Device selection not implemented')


class Selector(SelectorBase):
  """
  Selector classs

  #TODO: Add support for dropout
  What is Selector config ? A dict with the following params:
  selector_id : A unique identifier for each selector
  devices : dict corresponding to the devices selected for a given FL task
    device_id : device_ids of the devices
    device_comm: Communicator objects 

  The selector registers all devices that ping it to participate in the FL task,
  but only chooses certain number of devices that coordinator
  """

  def __init__(self, selector_config):
    self.selector_config = selector_config
    print(self.selector_config['devices'])

  def send_message(self,
                   message):
    logger.info('Sending Message {} to Device'.format(message.message_params))


  def select_devices(self, num_selected_devices_per_selector):
    """
    Select the number of devices specified by the server from the pool
    of registered devices
    :param num_selected_devices_per_selector: Num of selected devices for the FL task
    :return: None
    """
    for i, key in enumerate(self.selector_config['devices'].keys()):
      if i < num_selected_devices_per_selector:
