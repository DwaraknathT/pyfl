import os
import torch
import torch.distributed as dist
import torch.multiprocessing as mp
import torch.nn.functional as F
from torch.multiprocessing import Process, Pipe, Value

from core.args import get_args
from core.communication.message import Message
from core.communication.message_definitions import DeviceServerMessage, ServerDeviceMessage
from core.models.lenet import SimpleConvNet
from core.datasets import get_data
from core.utils import get_logger, setup_dirs
from core.device.device import Device
if torch.cuda.is_available():
  device = 'cuda'
else:
  device = 'cpu'

setup_dirs()
args = get_args()
logger = get_logger(__name__)

# SERVER_ID = Value('i',0)
device2server = DeviceServerMessage()
server2device = ServerDeviceMessage()


class Server:
  def run(self, comms):
    print('Server init')
    device_messages = []
    for con in comms:
      dev_msg = con.recv()
      device_messages.append(dev_msg)
      print(dev_msg.get_message_params())

    # coor_obj = Coordinator()
    # oor_obj.run()

'''
class Device:
  def __init__(self, model, dataset, task_config):
    print('Device init')
    self.model = model
    self.dataset = dataset
    print(dataset)
    self.optimizer = torch.optim.SGD(self.model.parameters(),
                                     lr=task_config['lr'])
    self.task_config = task_config

  def seng_message(self, comms, server_id):
    my_msg = Message({'sender_id': os.getpid(),
                      'receiver_id': server_id.value,
                      'message_class': device2server.D2S_NOTIF_CLASS,
                      'message_type': device2server.D2S_NOTIF_CLASS.D2S_NOT_READY,
                      'message': None})

    comms.send(my_msg)

  def train(self):
    self.model.train()
    for batch_idx, (data, target) in enumerate(self.dataset):
      data, target = data, target.to(device)
      self.optimizer.zero_grad()
      output = self.model(data)
      loss = F.nll_loss(output, target)
      loss.backward()
      self.optimizer.step()
      if batch_idx % 5 == 0:
        print('Train batch: {} Loss: {:.4f}'.format(
          batch_idx, loss.item()))

  def run(self):
    print('starting training')
    self.train()
'''

class Coordinator:
  def run(self, i=1):
    print("Coordinator is runnning \n")
    dataset_size = 100
    print("The number of batches per device {}".format(dataset_size // i))


def spawn_server(comms, server_id, dataset=None):
  serv = Server()
  server_id.acquire()
  server_id.value = os.getpid()
  server_id.release()
  serv.run(comms)


def spawn_device(comms, server_id, dataset):
  device_config={
    'device_id':os.getpid(),
    'server_id': server_id,
    'ready':0,
    'participate':0,
    'task_status':0,
    'update_local_model':0,
    'sync_server':0,
    'model':args.model,
    'optimizer': args.optim
  }
  logger.info("Spawning device with device config : {}".format(device_config))
  device = Device(device_config=device_config,
               dataset=dataset)
  device.run_device()


def run(rank, size, fn, comms, server_id):
  if rank != 0:
    trainset, testloader = get_data(args)
    fn(comms, server_id, trainset)
  else:
    fn(comms, server_id)


def init_process(rank, size, fn, comms, server_id=None, backend='gloo'):
  """ Initialize the distributed environment. """
  os.environ['MASTER_ADDR'] = '127.0.0.1'
  os.environ['MASTER_PORT'] = '29500'
  logger.info("MASTER_ADDR : {}".format(os.environ['MASTER_ADDR']))
  logger.info("MASTER_PORT : {}".format(os.environ['MASTER_PORT']))
  dist.init_process_group(backend, rank=rank, world_size=size)

  run(rank, size, fn, comms, server_id)


if __name__ == "__main__":
  mp.set_start_method('spawn')
  SERVER_ID = Value('i', 0)
  processes = []
  server_comm = []
  device_comm = []
  logger.info('Run arguments::{}'.format(vars(args)))

  for i in range(2):
    server_con, device_con = Pipe()
    server_comm.append(server_con)
    device_comm.append(device_con)
  for i in range(3):
    if i == 0:
      p = Process(target=init_process, args=(i, 3,
                                             spawn_server, server_comm,
                                             SERVER_ID))
    else:
      p = Process(target=init_process, args=(i, 3,
                                             spawn_device, device_comm[i - 1],
                                             SERVER_ID))
    p.start()
    processes.append(p)

  for p in processes:
    p.join()
