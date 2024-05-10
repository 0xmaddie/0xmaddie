import dataclasses

@dataclasses.dataclass(frozen=True)
class Optimizer:
  quota: int
  num_measurements: int
  state_capacity: int
  momentum_factor: float
  residual_factor: float
  weight_decay: float
  learning_rate: float

  def measure(self, machine, data):
    energy = 0
    for i in range(self.num_measurements):
      (init, eval)  = data()
      energy       += eval(machine(init))
    return energy/self.num_measurements

  def update(self, weights, gradient, momentum):
    next_momentum = self.interpolate(
      gradient,
      momentum,
      self.momentum_factor,
    )
    residual = self.interpolate(
      gradient,
      momentum,
      self.residual_factor,
    )
    mixture       = weights*self.weight_decay+sign(residual)
    weight_update = mixture*self.learning_rate
    return weight_update, next_momentum

  def __call__(self, initial_weights, constructor, data):
    weights  = []
    momentum = []
    energy   = []
    for _ in range(self.quota):
      for i in range(self.state_capacity):
        machine   = constructor(weights[i])
        energy[i] = self.measure(machine, data)
      average_weights  = self.average(weights, energy)
      average_machine  = constructor(average_weights)
      energy_threshold = self.measure(average_machine, data)
      for i in range(self.state_capacity):
        if energy[i] <= energy_threshold:
          continue
        compass  = weights[i]-average_weights
        sort     = compass*self.coherence
        search   = (compass@compass)*self.noise()
        gradient = sort+search
        weight_update, next_momentum = self.update(
          weights[i],
          momentum[i],
          gradient,
        )
        weights[i]  += weight_update
        momentum[i]  = next_momentum
    return self.average(weights, energy)
