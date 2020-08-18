from abc import ABC
from core.server.coordinator import Coordinator
from core.server.aggregator import AggregatorBase, MasterAggregatorBase
from core.server.selector import Selector

class ServerBase(ABC):
  """
  A parameter server that holds all actors in the server space.
  """
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


class Server(SelectorBase):
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
  """
  def __init__(self, server_config):
    super(Server, self).__init__()
    self.config = server_config
    self.coordinators = []
    self.selectors = []
    self.aggregators = []
    self.master_aggregators = []

  def spawn_selectors(self):
    """
    Spawns the number of selectors mentioned in the server
    config dict
    :return: None
    """
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
    for i in range(self.config['num_coordinators']):
      config = {
        'selector_id': i,
        'total_population': 0,
        'total_population_ids': [],
        'selected_population': 0,
        'selected_population_ids': []
      }
      self.selectors.append(Selector(selector_config=config))

  def get_config(self):
    """
    Returns the config file of this server
    :return: Server's config (dict)
    """
    return self.config



