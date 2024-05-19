# Studio

- [🛸 Lisp](#lisp)
- [Resonators](#resonators)
- [Media](#media)
- [Web](#web)
- [Llama](#llama)
- [♊ Gemini](#gemini)

## 🛸 Lisp

I think Lisp will be a good language for AI agents for a couple
reasons.

Macros (or in the case of Kernel, fexprs) let you make new languages
within Lisp. Some people don't like macros and feel it makes code
opaque or confusing, but I'm gonna assume that a language model will
have no problem with this type of thing and will actually appreciate
the reduced number of tokens it takes to express a concept.

Since synthetic data is a thing I'm hoping the fact that it's very
easy to generate symbolic expressions will help. When you view macros
as a code generation tool then there's overlap with synthetic data
generation, right?

I also wanna throw in delimited continuations because I feel it'll
help with composition. In fact, I'm wondering if I can set up a type
of complentary relationship between abstraction (the focus of the
Racket and Kernel philosophies about making new languages) and
composition (the focus of things like Jules Hedges' open games, of
functional programming in general etc). I'm wondering if the lens of
abstraction/composition is enough to make some progress on
interpretability of generative models, so it'd be cool to have it
expressed in the code interpreter attached to the models as well.

Also it's a little difficult to sandbox Python in Python and I want to
do things like control the amount of effort spent evaluating an
expression or restrict access to effects.

Here are the Lisp dialects I'm looking at:

- Common Lisp
- Emacs Lisp
- Scheme
- Guile
- Racket
- Clojure
- Kernel

Racket and Kernel really lean in to the idea that the essence of Lisp
is creating new programming languages. This is the main principle I
want to follow as well, as I think it combines nicely with generative
language models.

Racket and Emacs share the idea of the Lisp environment absorbing as
many operating system abilities as possible.

## 🐟 Resonators

![A school of fish in the shape of a fish.](../2024_05_07_1920.jpg)

A resonator is basically a program full of data races with a thread
scheduler trained on a dataset. The idea is that the average behavior
of the threads over time will approximate some implicitly defined
function provided by the loss during training. Each block of the
resonator runs a bunch of trials to try and get an average
measurement, and hopefully the output at the end approximates
something useful.

Another way to view it is that you can do program evolution with a
stack of "genetic transformer" blocks each containing fitness,
crossover, and mutation operations. Attach weighted coins to race all
of the operations and train this with a particle swarm on data showing
the evolutionary paths you want.

You can increase representational capacity by expressing conditional
dependence between the weights. So per block there are F fitness
weights, FxC crossover weights, FxCxM mutation weights representing
the prob that op will be next in line during its race, along with 1
residual.

The reason genetic programming never really took off but neural nets
did is bc genetic programming was just a bunch of random ops trying to
satisfy a loss. You gotta tune the ops first on data and then you'll
have "intelligent mutations" that can do goal conditioned evolution.

The crossovers combine several states in to one and the mutations
transform one state in to several. this acts as a type of information
bottleneck and provides an analogy to continuity in that it "smooths
out" the details between states.

It's called a resonator because [afaik the principle behind it is
related to stochastic resonance]().

## Media

## Web

## Llama
You know how you need to sample a language model a bunch of times to
get good responses? This is a wrapper class around the transformers
implementation of Llama 3 with some methods for "map/reduce" across
many Llama outputs.

## ♊ Gemini
