from abc import ABC


class MasterAggregatorBase(ABC):
  """
  Master aggregator abstract base class.
  Get the device list from coordinator, partition amongs the
  available set of aggregators.
  Manages aggregators in any given round, aggregates the
  updates from individual aggregators, updates the base.
  model
  """

  def __int__(self, **kwargs):
    """
    Master Aggregator initializer
    """
    raise NotImplementedError('Master aggregator not implemented')

  def pings_coordinator(self, **kwargs):
    """
    Pings the coordinator to get the device list ]
    """
    raise NotImplementedError('Aggregator-Coordinator interface not implemented')

  def spawn_aggregators(self, **kwargs):
    """
    Spawn generators based on the number of devices, task
    """
    raise NotImplementedError('Aggregator spawn not implemented')

  def sync_aggregator(self, **kwargs):
    """
    Sync the updates from the aggregators, update global model
    """
    raise NotImplementedError('Sync aggregators not implemented')


class AggregatorBase(ABC):
  """
  Aggregator abstract base class.
  Manages a set of devices registered to it, in a given round.
  Aggregates updates from the device and pushes to master
  """

  def __init__(self, **kwargs):
    """
    Initialize aggregator. Get the device list from master aggregator,
    and register them.
    """
    raise NotImplementedError('Aggregator not implemented')

  def ping_master(self, **kwargs):
    """
    Sends the aggregated updates to the master.
    """
    raise NotImplementedError('Aggregator-Master interface not implemented')

  def sync_devices(self, **kwargs):
    """
    Reach out to the selected devices, gets updates, makes sure
    they are in sync.
    """
    raise NotImplementedError('Sync devices connected to this aggregator')
