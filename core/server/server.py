import abc
import copy
from abc import ABC

from core.args import get_args
from core.communication.message_definitions import DeviceServerMessage, ServerDeviceMessage
from core.communication.message_definitions import DeviceServerNotifClass
from core.server.selector import Selector
from core.utils import get_logger

logger = get_logger(__name__)
device2server = DeviceServerMessage()
server2device = ServerDeviceMessage()

args = get_args()


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
    self.devices = {}
    self.coordinators = []
    self.selectors = []
    self.aggregators = []
    self.master_aggregators = []
    self.comms = comms

  def spawn_selectors(self, num_selectors):
    """
    Spawns the number of selectors ( a pre-determined constant) mentioned in the server
    config dict
    :return: None
    """
    logger.info('Spawning {} selectors'.format(num_selectors))
    devices_per_selector = []
    curr_dict = {}
    for k, v in self.devices.items():
      if len(curr_dict.keys()) < args.max_devices_per_selector:
        curr_dict.update({k: v})
      else:
        devices_per_selector.append(copy.deepcopy(curr_dict))
        curr_dict = {k: v}
    # update last curr_dict
    devices_per_selector.append(curr_dict)
    for i in range(num_selectors):
      config = {
        'selector_id': i,
        'devices': devices_per_selector[i]
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
        'total_num_devices': i,
        'num_devices_per_selector': 0,
        'num_selectors': [],
        'num_devices_per_aggregator': 0,
        'num_aggregators': []
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

  def calculate_num_workers(self, num_devices):
    """
    Returns the total number of devices required per FL task
    :param num_devices: Total number of devices registered in a given round
    :return: num_devices_for_task
    """
    num_devices_for_task = num_devices
    return num_devices_for_task

  def get_config(self):
    """
    Returns the config file of this server
    :return: Server's config (dict)
    """
    return self.config

  def recv_messages(self):
    device_messages = []
    for connection in self.comms:
      dev_msg = connection.recv()
      if isinstance(dev_msg.message_class, DeviceServerNotifClass) and (dev_msg.message_type == 1):
        self.devices[dev_msg.sender_id] = connection
      device_messages.append(dev_msg)
      logger.info('Message received from Device {}: {}'.format(dev_msg.message_params,
                                                               dev_msg.message_params['receiver_id']))
    return device_messages

  def run_server(self):
    # spawn all related stuff
    # self.spawn_selectors()
    # self.spawn_coordinators()
    # self.spawn_aggregators()
    # self.spawn_master_aggregators()

    device_participation_messages = self.recv_messages()
    num_devices = len(self.devices)
    num_selectors = num_devices // args.max_devices_per_selector
    self.spawn_selectors(num_selectors)
    num_selected_devices = self.calculate_num_workers(num_devices)
    num_selected_devices_per_selector = num_selected_devices // num_selectors
