# from core.utils import get_data, make_data_partition
# from core.args import get_args
# import numpy as np

import os

# from mpi4py import MPI
import torch
import torch.distributed as dist
import torch.multiprocessing as mp
import torch.nn.functional as F
from torch.multiprocessing import Process, Pipe, Value

from core.args import get_args
from core.communication.message import Message
from core.communication.message_definitions import DeviceServerMessage, ServerDeviceMessage
from core.models.lenet import SimpleConvNet
from core.utils import get_data

if torch.cuda.is_available():
  device = 'cuda'
else:
  device = 'cpu'

args = get_args()

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
  task_config = {
    'lr': 0.001,
    'epochs': 1
  }
  dev = Device(model=SimpleConvNet(),
               dataset=dataset,
               task_config=task_config)
  dev.run()


def run(rank, size, fn, comms, server_id):
  if rank != 0:
    trainset, testloader = get_data(args)
  fn(comms, server_id, trainset)


def init_process(rank, size, fn, comms, server_id=None, backend='gloo'):
  """ Initialize the distributed environment. """
  os.environ['MASTER_ADDR'] = '127.0.0.1'
  os.environ['MASTER_PORT'] = '29500'
  dist.init_process_group(backend, rank=rank, world_size=size)

  run(rank, size, fn, comms, server_id)


if __name__ == "__main__":
  mp.set_start_method('spawn')
  SERVER_ID = Value('i', 0)
  processes = []
  server_comm = []
  device_comm = []

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
