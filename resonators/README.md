![A robotic school of fish.](../2024_05_05_1917.jpg)

[**Resonators**](https://github.com/0xmaddie/0xmaddie/blob/main/resonators)
is a Python library that uses data races and particle swarm dynamics
to approximate functions. You can train a resonator like a transformer
but it uses Python objects instead of vectors.

## Getting started

```python
inputs  = []
outputs = []
model   = resonators.Decoder(weights)
final   = model(initial)
```

## Particle swarms and oracle machines
How does "swarm intelligence" work? A logical dependence on an
implicit function representation observed by repeated measurement of
collective behavior is a type of non-algorithmic computation bc
there's no effective procedure that would give you that information.

You can use a particle swarm to train something called a component
system — like a Turing machine or a bunch of Python or Lisp functions
— in a manner similar to a neural net. The idea is to use the
priorities of racing threads as an implicit representation of an
energy function learned from a dataset.

The important part is that each individual thread operation can only
use data that is averaged across every thread. This provides an
analogy to continuity and allows you to pass to the mean field limit,
so you can optimize in a manner similar to a neural net.

Imagine a class of programs written as lists of rules of the following
form: If the state has a certain property, transform the state in a
certain way. To execute these programs, evaluate the conditions in the
order they are written until one is true, and then apply the
corresponding transformation.

We'd like to add weights to the space of all possible programs of this
shape and tune them in alignment with a dataset. In other words, we'd
like to create an oracle machine. The resonator is a machine of this
type that uses an analogy to continuous functions through particle
swarm dynamics to explore this space of programs.

The resonator contains lists of every possible property and
transformation, respectively called the "inputs" and the
"outputs". When a layer is presented with a swarm of states, the
inputs race according to their advice. The advice is provided in the
form of the bias of a coin; on each step of the race the coins
represent the probability that the respective input will be next in
line until the inputs are sorted.

Then, in the sorted order, the inputs attempt to provide a measurement
of the swarm states that satisfy some property. If an input is unable
to provide the minimum number of states required for a measurement,
then the search proceeds with the next input in line. If no inputs are
able to provide a measurement, the procedure raises an exception.

If the inputs are able to provide a measurement, then the outputs
condition on the winner of the input race and perform their own race
in the same manner. The winner of the output race then combines the
entire measurement of states into a single state in a manner similar
to a crossover operation from genetic programming. It's important that
the output's final state depends on many states sampled from the swarm
at once in order to provide the analogy to continuity.

This input-output process is repeated until a measurement of states
has been provided by the outputs. Then, this measurement races with
the initial states according to the advice as a type of residual
connection. The idea is that the probabilities of all of these events
are an implicit representation of a function learned from a
dataset. In this sense, the coins are an oracle provided to a machine
allowing it to self-organize.
