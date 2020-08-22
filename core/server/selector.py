from abc import ABC


class SelectorBase(ABC):
  """
  Selector abstract base class
  """

  def __init__(self, **kwargs):
    """
    Initialize the selector
    """
    raise NotImplementedError('Selector initializer not implemented')

  def ping_coordinator(self, **kwargs):
    """
    Ping the coordinator to get the task info and number of devices,
    required.
    """
    raise NotImplementedError('Coordinator selector interface not implemented')

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
  * Selector id : A unique identifier for each selector
  * total_population : Total number of devices that established bi-directional comm
    channel with selector (int)
  * total_population_ids : Ihe ids of all devices registered to the selector
  * selected_population : Total number of devices determined chosen or a given FL task (int)
  * selected_population_ids : The ids of all devices participating in the FL task

  The selector registers all devices that ping it to participate in the FL task,
  but only chooses certain number of devices that coordinator
  """
  def __init__(self, selector_config):
    super(Selector, self).__init__()
    self.selector_config = selector_config

