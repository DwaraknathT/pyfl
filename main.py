import os

import loguru
import torch
import torch.backends.cudnn as cudnn
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.multiprocessing import Process, Pipe, Value

from core.args import get_args
from core.communication.message_definitions import DeviceServerMessage, ServerDeviceMessage
from core.datasets import get_data
from core.device.device import Device
from core.server.server import Server
from core.utils import get_logger, setup_dirs

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

'''
class Server:
  def run(self, comms):
    print('Server init')
    device_messages = []
    for con in comms:
      dev_msg = con.recv()
      message = Message({
        'sender_id': os.getpid(),
        'receiver_id': 0,
        'message_class': server2device.S2D_NOTIF_CLASS,
        'message_type': server2device.S2D_NOTIF_CLASS.S2D_SELECTED,
        'message': None
      })
      con.send(message)
      device_messages.append(dev_msg)
      print(dev_msg.get_message_params())

    # coor_obj = Coordinator()
    # oor_obj.run()


""" Gradient averaging. """

def average_gradients(model):
  size = float(dist.get_world_size())
  for param in model.parameters():
    dist.all_reduce(param.grad.data,
                    group=dist.new_group([x for x in range(1, int(size))]),
                    op=dist.ReduceOp.SUM)
    param.grad.data /= (size - 1)


class Device:
  def __init__(self, model, dataset, task_config):
    print('Device init')
    self.model = model.to(device)
    self.dataset = dataset
    self.criterion = torch.nn.CrossEntropyLoss()
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
    correct = 0
    for batch_idx, (data, target) in enumerate(self.dataset['trainset']):
      data, target = data.to(device), target.to(device)
      self.optimizer.zero_grad()
      output = self.model(data)
      loss = self.criterion(output, target)
      loss.backward()
      average_gradients(self.model)
      self.optimizer.step()
      pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
      correct += pred.eq(target.view_as(pred)).sum().item()
      if batch_idx % 100 == 0:
        print('Train batch: {} Loss: {:.4f} Accuracy: {:.0f}%'.format(
          batch_idx, loss.item(), 100. * correct / len(self.dataset['testset'].dataset)))

  def test(self):
    self.model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
      for data, target in self.dataset['testset']:
        data, target = data.to(device), target.to(device)
        output = self.model(data)
        test_loss += self.criterion(output, target).item()  # sum up batch loss
        pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
        correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(self.dataset['testset'].dataset)

    print('\nTest set: Average loss: {:.4f}, Accuracy: {:.0f}%\n'.format(
      test_loss, 100. * correct / len(self.dataset['testset'].dataset)))

  def run(self):
    print('starting training')
    self.train()
    self.test()
'''


class Coordinator:
  def run(self, i=1):
    print("Coordinator is runnning \n")
    dataset_size = 100
    print("The number of batches per device {}".format(dataset_size // i))


def spawn_server(comms, server_id, dataset=None):
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
                  comms=comms)
  server.run_server()
  # serv.run(comms)


def spawn_device(comm, server_id, dataset):
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
  device = Device(device_config=device_config,
                  comm=comm,
                  dataset=dataset)
  device.run_device()
  """
  device = Device(SimpleConvNet(),
                  dataset,
                  {'lr': 0.01})
  device.run()
  """


def run(rank, size, fn, comms, server_id):
  if rank != 0:
    dataset = {}
    dataset['trainset'], dataset['testset'] = get_data(args)
    fn(comms, server_id.value, dataset)
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
  size = args.num_devices

  for i in range(size):
    server_con, device_con = Pipe()
    server_comm.append(server_con)
    device_comm.append(device_con)
  for i in range(size + 1):
    if i == 0:
      p = Process(target=init_process, args=(i, (size + 1),
                                             spawn_server, server_comm,
                                             SERVER_ID))
    else:
      p = Process(target=init_process, args=(i, (size + 1),
                                             spawn_device, device_comm[i - 1],
                                             SERVER_ID))
    p.start()
    processes.append(p)

  for p in processes:
    p.join()
