from abc import ABC
from core.server.coordinator import CoordinatorBase
from core.server.aggregator import AggregatorBase, MasterAggregatorBase
from core.server.selector import SelectorBase

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

