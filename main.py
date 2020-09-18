import os

import torch
import torch.backends.cudnn as cudnn
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.multiprocessing import Process, Value

from pyfl.args import get_args
from pyfl.communication.communicator import Communicator
from pyfl.communication.message_definitions import DeviceServerMessage, ServerDeviceMessage
from pyfl.datasets import get_data
from pyfl.device.device import Device
from pyfl.server.server import Server
from pyfl.utils import get_logger, setup_dirs

if torch.cuda.is_available():
  device = 'cuda'
  cudnn.benchmark = True
else:
  device = 'cpu'

setup_dirs()
args = get_args()
logger = get_logger(__name__)

# SERVER_ID = Value('i',0)
device2server = DeviceServerMessage()
server2device = ServerDeviceMessage()

class Coordinator:
  def run(self, i=1):
    print("Coordinator is runnning \n")
    dataset_size = 100
    print("The number of batches per device {}".format(dataset_size // i))


def spawn_server(communicator, server_id, dataset=None):
  server_id.acquire()
  server_id.value = os.getpid()
  server_id.release()

  server_config = {
    'server_id': server_id.value,
    'num_selectors': 1,
    'num_coordinators': 1,
    'num_master_aggregators': 1,
    'num_aggregators': 1,
    'rounds': 1,
    'run_args': args
  }
  logger.info("Spawning server with device config : {}".format(server_config))
  server = Server(server_config,
                  communicator=communicator)
  server.run_server()


def spawn_device(communicator, server_id, dataset):
  device_config = {
    'device_id': os.getpid(),
    'server_id': server_id,
    'ready': 0,
    'participate': 0,
    'task_status': 0,
    'update_local_model': 0,
    'sync_server': 0,
    'model': args.model,
    'optimizer': args.optim
  }
  logger.info("Spawning device with device config : {}".format(device_config))
  communicator.register(device_config['device_id'], server_id)
  device = Device(device_config=device_config,
                  dataset=dataset,
                  communicator=communicator)
  device.run_device()

def run(rank, communicator, fn, server_id):
  if rank != 0:
    dataset = {}
    dataset['trainset'], dataset['testset'] = get_data(args)
    fn(communicator, server_id.value, dataset)
  else:
    fn(communicator, server_id)


def init_process(rank, size, communicator,
                 fn, server_id=None, backend='gloo'):
  """ Initialize the distributed environment. """
  os.environ['MASTER_ADDR'] = '127.0.0.1'
  os.environ['MASTER_PORT'] = '29500'
  logger.info("MASTER_ADDR : {}".format(os.environ['MASTER_ADDR']))
  logger.info("MASTER_PORT : {}".format(os.environ['MASTER_PORT']))
  dist.init_process_group(backend, rank=rank, world_size=size)

  run(rank, communicator, fn, server_id)


if __name__ == "__main__":
  mp.set_start_method('spawn')
  SERVER_ID = Value('i', 0)
  processes = []
  logger.info('Run arguments::{}'.format(vars(args)))
  size = args.num_devices

  communicator = Communicator()
  for i in range(size + 1):
    if i == 0:
      p = Process(target=init_process, args=(i, (size + 1), communicator,
                                             spawn_server,
                                             SERVER_ID))
    else:
      p = Process(target=init_process, args=(i, (size + 1), communicator,
                                             spawn_device,
                                             SERVER_ID))
    p.start()
    processes.append(p)

  for p in processes:
    p.join()
