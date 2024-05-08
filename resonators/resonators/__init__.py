import numpy
import scipy

class Decoder:
  fitness: list[callable]
  crossover: list[callable]
  mutation: list[callable]
  weights: numpy.ndarray
  state_capacity: int
  state_bottleneck: int

  def __init__(
    self,
    fitness: list[callable],
    crossover: list[callable],
    mutation: list[callable],
    weights: numpy.ndarray,
    state_capacity: int,
    state_bottleneck: int,
  ):
    self.fitness          = fitness
    self.crossover        = crossover
    self.mutation         = mutation
    self.weights          = weights
    self.state_capacity   = state_capacity
    self.state_bottleneck = state_bottleneck

    assert len(weights) == self.layers*self.weights_per_layer

  @staticmethod
  def num_weights_for_components(fitness, crossover, mutation, layers):
    fitl   = len(fitness)
    crossl = len(fitness)*len(crossover)
    mutl   = len(fitness)*len(crossover)*len(mutation)
    return layers*(fitl+crossl+mutl+1)

  @property
  def weights_per_layer(self):
    return self.fitness_weights_per_layer+self.crossover_weights_per_layer+self.mutation_weights_per_layer+1

  @property
  def layers(self):
    return len(self.weights)//self.weights_per_layer

  @property
  def fitness_weights_per_layer(self):
    return len(self.fitness)

  @property
  def crossover_weights_per_layer(self):
    return len(self.fitness)*len(self.crossover)

  @property
  def mutation_weights_per_layer(self):
    return len(self.fitness)*len(self.crossover)*len(self.mutation)

  def fitness_weights(self, layer):
    lhs = layer*self.weights_per_layer
    return self.weights[lhs:lhs+self.fitness_weights_per_layer]

  def crossover_weights(self, layer, fitness):
    lhs = layer*self.weights_per_layer+self.fitness_weights_per_layer
    return self.weights[lhs:lhs+self.crossover_weights_per_layer]

  def mutation_weights(self, layer, fitness, crossover):
    lhs = layer*self.weights_per_layer+self.fitness_weights_per_layer+self.crossover_weights_per_layer
    return self.weights[lhs:lhs+self.mutation_weights_per_layer]

  def residual_weights(self, layer):
    lhs = layer*self.weights_per_layer+self.fitness_weights_per_layer+self.crossover_weights_per_layer+1
    return self.weights[lhs]

  def race(self, components, weights):
    sorted_components = numpy.random.choice(
      components,
      size=len(components),
      replace=False,
      p=self.__softmax(weights),
    )
    return sorted_components

  def __softmax(self, array):
    return scipy.special.softmax(array)

  def __coin(self, weight):
    return numpy.random.random() < weight

  def __choice(self, components):
    return numpy.random.choice(components)

  def __call__(self, states):
    for layer in range(self.layers):
      hidden_states = []
      for i in range(self.state_capacity):
        sorted_fitness = self.race(
          self.fitness,
          self.fitness_weights(layer),
        )
        fitness_hidden      = []
        current_fitness_id  = 0
        selected_fitness_id = None
        while selected_fitness_id is None and current_fitness_id < len(self.fitness):
          local_fitness = sorted_fitness[current_fitness_id]
          fitness_hidden.clear()
          for state in states:
            if local_fitness(state):
              print(f'Decoder current_fitness_id {current_fitness_id} {state} True')
              fitness_hidden.append(state)
              if len(fitness_hidden) >= self.state_bottleneck:
                selected_fitness_id = current_fitness_id
                break
            else:
              print(f'Decoder current_fitness_id {current_fitness_id} {state} False')
          current_fitness_id += 1
        if selected_fitness_id is None:
          raise ValueError(f'No fitness operation available')
        assert len(fitness_hidden) == self.state_botteneck
        print(f'Decoder.fitness_hidden = {fitness_hidden} Ok')
        sorted_crossover = self.race(
          self.crossover,
          self.crossover_weights(layer, selected_fitness_id),
        )
        crossover_hidden      = None
        current_crossover_id  = 0
        selected_crossover_id = None
        while selected_crossover_id is None and current_crossover_id < len(self.crossover):
          local_crossover = sorted_crossover[current_crossover_id]
          try:
            crossover_hidden      = functools.reduce(local_crossover, fitness_hidden)
            selected_crossover_id = current_crossover_id
          except ValueError as err:
            print(f'Decoder.current_crossover_id {current_crossover_id} Err')
            current_crossover_id += 1
        if selected_crossover_id is None:
          raise ValueError('No crossover operation available')
        assert crossover_hidden is not None
        print(f'Decoder.crossover_hidden = {crossover_hidden} Ok')
        sorted_mutation = self.race(
          self.mutation,
          self.mutation_weights(layer, selected_fitness_id, selected_crossover_id)
        )
        mutation_hidden      = []
        current_mutation_id  = 0
        selected_mutation_id = None
        while selected_mutation_id is None and current_mutation_id < len(self.mutation):
          local_mutation = sorted_mutation[current_mutation_id]
          try:
            mutation_hidden.clear()
            for j in range(self.state_bottleneck):
              point = local_mutation(crossover_hidden)
              mutation_hidden.append(point)
            selected_mutation_id = current_mutation_id
          except ValueError as err:
            print(f'Decoder.current_mutation_id {current_mutation_id} Err')
            current_mutation_id += 1
        if selected_mutation_id is None:
          raise ValueError('No mutation operator available')
        assert len(mutation_hidden) == self.state_bottleneck
        print(f'Decoder.mutation_hidden {mutation_hidden}')
        hidden_states += mutation_hidden
      target_states = []
      residual      = self.residual_weights(layer)
      for i in range(self.state_capacity):
        if self.__coin() < residual:
          state = self.__choice(states)
          print(f'Decoder residual state {state}')
        else:
          state = self.__choice(hidden_states)
          print(f'Decoder hidden state {state}')
        target_states.append(state)
      print(f'Decoder.target_states {target_states}')
      states = target_states
    return states

'''
@dataclasses.dataclass(frozen=True)
class Optimizer:
  facc: float
  fres: float
  rate: float
  decay: float

  def __call__(self, pos, acc, grad):
    hacc  = self.interp(grad, acc, self.facc)
    res   = self.interp(grad, acc, self.fres)
    mix   = pos*self.decay+sign(res)
    delta = mix*self.rate
    return delta, hacc

class Tuner:
  quota: int
  purity: int
  density: int
  update: callable

  def measure(self, machine, data):
    energy = 0
    for i in range(self.purity):
      (init, eval)  = data()
      energy       += eval(machine(init))
    return energy/self.purity

  def __call__(self, init, cons, data):
    pos  = []
    acc  = []
    loss = []
    for _ in range(self.quota):
      for i in range(self.density):
        machine = cons(pos[i])
        loss[i] = self.measure(machine, data)
      center  = self.average(pos, loss)
      teacher = cons(center)
      cutoff  = self.measure(teacher, data)
      for i in range(self.density):
        if loss[i] <= cutoff:
          continue
        compass  = pos[i]-center
        sort     = compass*self.coherence
        search   = (compass@compass)*self.noise()
        gradient = sort+search
        vel, acc = self.update(pos[i], acc[i], gradient)
        pos[i]  += vel
        acc[i]   = acc
    return self.average(pos, loss)
'''
