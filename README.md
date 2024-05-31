Hi I'm **Maddie**.

[Programming as theory building, language = machines + signs]

With this in mind, consider the following quote from John Locke:

> The acts of the mind, wherein it exerts its power over its simple
> ideas, are chiefly these three: (1) Combining several simple ideas
> into one compound one; and thus all complex ideas are made. (2) The
> second is bringing two ideas, whether simple or complex, together,
> so as to take a view of them at once, without uniting them into one;
> by which way it gets all its ideas of relations. (3) The third is
> separating them from all other ideas that accompany them in their
> real existence: this is called abstraction: and thus all its general
> ideas are made.

— John Locke, An Essay Concerning Human Understanding ([Lo1690]),
Bk. II Ch. xii §1.1

In light of *Programming as theory building*, you can view this quote
as the initial seed of a computational ideology with three
foundational principles: **abstraction**, **composition**, and
**relation**.

A programming language is a notation for cognitive work, so it makes
sense that Lisp would have a major feature directly addressing the
three acts.

For abstraction, **macros**. For composition, **coroutines**. For
relation, **cookies**.

**🧭 Macros**

A **macro**

```
(def lambda
  (vau xs lexical
    (let ((args (fst xs))
	      (body (snd xs))
		  (expr (list* vau args :none body)))
      (wrap (eval expr lexical)))))
```

**🚦 Coroutines**

- A **coroutine**

- Coroutines/generators in Lua, Python, and JavaScript are **one-shot**.

- Lisp coroutines are **many-shot**.

```
(label ()
  (yield (lambda (go) (go 5))))
```

This is a renamed [`shift`/`reset`]() i.e. [delimited continuations]().

**🥠 Cookies**

A **cookie**

```
(label (((contains? print?) (replace my-print)))
  (some-procedure))
```

This is a new mechanism that I just made up; the original name was
"advice" but then I realized a fortune cookie gives you advice? and
cookies is a more interesting name.

[💌 Sign theory](https://sweetp.xyz/sign-theory) — I think if you read
Brian Cantwell Smith's [Meaning & Mechanism]() and Webb Keane's
[Semiotics and the social analysis of material things]() back-to-back,
you'll see that Peirce is describing the theory that Smith repeatedly
says he's unable to provide, which means [semiotics]() — like
[physics](https://constructortheory.org) — is one of the many fields
that computer science must absorb in order to reach its true
potential.

[♎ Constructor theory](https://sweetp.xyz/constructor-theory)
