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
