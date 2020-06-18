"""Parameter Server distributed training with Ray."""

import ray
from wasabi import msg
from .. import util

class OptimizerWorker:
    def __init__(self, config_path, world_size, sync=True):
        self.optimizer = _create_optimizer(config_path)
        self.weights_dict = {}
        self.world_size = world_size
        self.sync = sync

    def call(self, rank, key, weights, gradient, *, lr_scale=1.0):
        if key not in self.weights_dict:
            self.weights_dict[key] = weights.copy()
        new_weights, new_grads = self.optimizer(
            key, self.weights_dict[key], gradient.copy(), lr_scale=lr_scale)
        self.weights_dict[key] = new_weights
        return new_weights, new_grads

    def fetch(self):
        return self.optimizer

    def step_schedules(self):
        self.optimizer.step_schedules()

class RayOptimizer:
    local_optimizer = None

    def __init__(self, config_path, use_gpu, rank):
        RemoteOptimizer = ray.remote(OptimizerWorker)
        if use_gpu >= 0:
            RemoteOptimizer = RemoteOptimizer.options(num_gpus=0.1)
        self.optimizer = RemoteOptimizer.remote(config_path)
        self.rank = rank
        self.sync()

    def sync(self):
        self.local_optimizer = ray.get(self.optimizer.fetch.remote())

    def __call__(self, *args, **kwargs):
        weights, grads = ray.get(self.optimizer.call.remote(self.rank, *args, **kwargs))
        return weights.copy(), grads.copy()

    def __getattr__(self, name):
        return getattr(self.local_optimizer, name)

    def step_schedules(self):
        self.optimizer.step_schedules.remote()
        self.sync()
