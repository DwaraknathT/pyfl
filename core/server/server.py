import abc
from abc import ABC

import loguru

from core.communication.message_definitions import DeviceServerMessage, ServerDeviceMessage
from core.server.selector import Selector
from core.utils import get_logger

log = loguru.logger

logger = get_logger(__name__)
device2server = DeviceServerMessage()
server2device = ServerDeviceMessage()


class ServerBase(ABC):
  """
  A parameter server that holds all actors in the server space.
  """
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def __init__(self, **kwargs):
    """
    Server initialization
    """
    raise NotImplementedError('Server base class not Implemented')

  def round(self, **kwargs):
    """
    Performs 1 round in FL task
    """
    raise NotImplementedError('Round not implemented')


class Server(ServerBase):
  """
  Server
  The server is the container that manages all instances of
  coordinators, selectors, aggregators, master aggregators
  The device sees only the server and none of the abstractions
  inside it.

  What is Server config ? A dict with the following params:
  server_id : A unique identifier for this server (int)
  num_selectors : The number of selectors in use (int)
  num_coordinators : The number of coordinators in use (int)
  num_master_aggregators : The number of master aggregators in use (int)
  num_aggregators : The number of aggregators in use (int)
  rounds : Number of rounds the FL task is run for (int)

  Server2Device message system:
  Message Class : what it does
  0 : Class of Notification messages from server to device
    0 : Notify the device it's selected
    1 : Notify the device to try later
  1 : Class of Query messages from server to device
    0 : Query the device if it's alive
    1 : Query the device if it's ready
  2 : Send the device some stuff
    0 : Send the global model
    1 : Send the task config
    2 : Send the task metrics
    #TODO: checkpoint stuff
  """

  def __init__(self,
               server_config,
               comms):
    self.config = server_config
    self.coordinators = []
    self.selectors = []
    self.aggregators = []
    self.master_aggregators = []
    self.comms = comms

  def spawn_selectors(self):
    """
    Spawns the number of selectors mentioned in the server
    config dict
    :return: None
    """
    logger.info('Spawning {} no of selectors'.format(self.config['num_selectors']))
    for i in range(self.config['num_selectors']):
      config = {
        'selector_id': i,
        'total_population': 0,
        'total_population_ids': [],
        'selected_population': 0,
        'selected_population_ids': []
      }
      self.selectors.append(Selector(selector_config=config))

  def spawn_coordinators(self):
    """
    Spawns the number of coordinators mentioned in the server
    config dict
    :return: None
    """
    logger.info('Spawning {} no of coordinators'.format(self.config['num_coordinators']))
    for i in range(self.config['num_coordinators']):
      config = {
        'selector_id': i,
        'total_population': 0,
        'total_population_ids': [],
        'selected_population': 0,
        'selected_population_ids': []
      }
      self.coordinators.append(Selector(selector_config=config))

  def spawn_aggregators(self):
    """
    Spawns the number of aggregators mentioned in the server
    config dict
    :return: None
    """
    logger.info('Spawning {} no of aggregators'.format(self.config['num_aggregators']))
    for i in range(self.config['num_aggregators']):
      config = {
        'selector_id': i,
        'total_population': 0,
        'total_population_ids': [],
        'selected_population': 0,
        'selected_population_ids': []
      }
      self.aggregators.append(Selector(selector_config=config))

  def spawn_master_aggregators(self):
    """
    Spawns the number of aggregators mentioned in the server
    config dict
    :return: None
    """
    logger.info('Spawning {} no of master aggregators'.format(self.config['num_master_aggregators']))
    for i in range(self.config['num_master_aggregators']):
      config = {
        'selector_id': i,
        'total_population': 0,
        'total_population_ids': [],
        'selected_population': 0,
        'selected_population_ids': []
      }
      self.master_aggregators.append(Selector(selector_config=config))

  def get_config(self):
    """
    Returns the config file of this server
    :return: Server's config (dict)
    """
    return self.config

  def run_server(self):
    # spawn all related stuff
    self.spawn_selectors()
    self.spawn_coordinators()
    self.spawn_aggregators()
    self.spawn_master_aggregators()

    self.recv_messages()
