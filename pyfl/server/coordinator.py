import abc
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

  def init_task_config(self, **kwargs):
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


class Coordinator(CoordinatorBase):
  """
  Coordinator

  What is coordinator_config? A dictionary with the following params:
  total_num_devices: Total number of devices 
  num_devices_per_aggregator: Maximum limit to the number of devices an aggregator handles
  num_aggregators: decided based on total_num_devices and num_devices_per_aggregator
  """
  def __init__(self, coordinator_config):
    self.config = coordinator_config


  def init_task_config(self):
    """
    Initializes the population based on the given task 
    (i.e, #devices required 

    What is task config? A dictionary with the following params:
    task_name: Name of the task being executed on the device
      train: run training on the device
      inference: run inference on the device
    model: Model architecture to be used by the devices
      eg: vgg11, vgg11_bn, resnet20, lenet, simplenet
    optimizer: Optimizer to use
    epochs: Number of epochs to train (if train), else None
    lr_params: Learning rate params
      lr_schedule: LR scheduler to use, eg: multi_step, cyclical
      initial_lr: initial learning rate
      up_step: up step size for cyclical lr, else None
      down_step: down step size for cyclical lr, else None
    metrics: dict of metrics to be returned by the device
      eg: accuracy, nll, error, bleu
    """