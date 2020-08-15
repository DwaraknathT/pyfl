from abc import ABC


class CoordinatorBase(ABC):
  """
  Coordinator abstract base class
  """

  def __init__(self, **kwargs):
    """
    Initializes coordinator
    TODO: see if you need coordinator id
    """
    raise NotImplementedError('Initializer not implemented')

  def init_task_plan(self, **kwargs):
    """
    Initializes the population based on the given task
    """
    raise NotImplementedError('Population initializer not implemented')

  def ping_selector(self, **kwargs):
    """
    Ping the selector to get the devices participating in the
    round
    """
    raise NotImplementedError('Selector-coorinator interface not implemetned')

  def register_devices(self, **kwargs):
    """
    Registers the list of devices returned by selector,
    also register them with aggregators
    """
    raise NotImplementedError('Device registry not implemented')

  def spawn_aggregators(self, **kwargs):
    """
    Given a set of registered devices spawn aggregators to send
    and receive updates
    """
    raise NotImplementedError('Aggregator spawn not implemented')

  def global_sync(self, **kwargs):
    """
    Global sync to make sure all devices are done with their round
    """
    raise NotImplementedError('Global sync not implemented')
