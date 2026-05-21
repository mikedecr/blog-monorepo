---
title: Using dark magic to create local scopes in Python
author: Michael DeCrescenzo
date: 2026-05-20T00:00:00.000Z
engine: knitr
knitr:
  opts_chunk:
    collapse: true
---


Although Python is descended from the C universe, it doesn't have the same scoping expectations.
This will surprise a user when they are writing a for-loop and the symbol that binds the iterand[^1] escapes the loop.

``` python
for i in range(5):
    x = i + 1

# is there an i out here? yes.
print(i)
## 4
```

Contrast to C where you cannot reach a variable outside of some scope block.

``` c
{
    int x = 1;
}

printf("%d", x);  // this would fail to compile
```

R has similar behavior as Python, but I never noticed it when I was an active R user.
Idiomatic R often encourages `apply` functions over loops.

``` r
# I am honestly kinda surprised that R does this.
for (i in 1:5) {
    x = i + 1
}
print(i)
## [1] 5

# but for some reason I find this less surprising
{
    a = 1
}
print(a)
## [1] 1
```

## But what if I told you...

You can actually achieve the feeling of local scope in Python with a little audacity.

In this example, we `Bind` the value `1` to symbol `a` in a `with` block.

``` python
with Bind(1) as a:
    print(a + 1)
## 2
```

But when we are outside the block again, `a` is gone.

``` python
a
## NameError: name 'a' is not defined
```

How is it possible?

If you think about it, we cannot simply `del` the variable inside the definition of the `with` block.
This deletes only the binding of the name `value` inside the scope of the function.

``` python
from contextlib import contextmanager

@contextmanager
def Local(value):
    yield value
    del value
    try:
        print(value)
    except NameError as e:
        print(e)

with Local("hi") as z:
    print(z + " in context")
## hi in context
## cannot access local variable 'value' where it is not associated with a value
```

But since the variable is bound `as z` outside the function scope, the binding in that scope sticks around.

``` python
# we don't want this to work, but it will work.
z + " outside context"
## 'hi outside context'
```

To add insult to injury, we can mutate the value inside the context, and it affects the value outside.
Because these are two separate bindings to the same object; there is no copy-on-modify behavior.

``` python
with Local(1) as a:
    a += 1
## cannot access local variable 'value' where it is not associated with a value

print(a)
## 2
```

## How do we actually do it?

Weep if you must.
Let's write it long-hand without the decorator.

``` python
class Bind:
    def __init__(self, *values, verbose=False):
        self._values = values
        self._verbose = verbose
        self._globals = globals()
        self._before = set(self._globals.keys())

    def __enter__(self):
        # len-1 tuple should feel like a single value to the user
        return self._values if len(self._values) > 1 else self._values[0]

    def __exit__(self, *args):
        # first K names are the `as` bindings
        all_new_names = [k for k in self._globals if k not in self._before]
        bindings = all_new_names[:len(self._values)]
        if self._verbose:
            print("all new names: " + str(all_new_names))
            print("bindings to clean: " + str(bindings))
        for name in bindings:
            if self._verbose:
                print("deleting " + name)
            del self._globals[name]
```

We take a snapshot of `globals()` (a dict that holds all global-scope name bindings) before and after we do our work in the context block.
Any new names that appear in the process must have been created in the context block.
So we delete those items from `globals()`, and when we exit the context block, we can't use those names to lookup data anymore.

I will turn on `verbose` mode for the next example to see the sequence of events.

``` python
with Bind(300, 400, verbose=True) as (A, B):
    extra = A + B
## all new names: ['A', 'B', 'extra']
## bindings to clean: ['A', 'B']
## deleting A
## deleting B

# fail successfully
try:
    print((A, B))
except NameError as e:
    print(e)
## name 'A' is not defined

# can still access this
print(extra)
## 700
```

This reveals some quirks in our implementation.

- Any new binding we create inside the context block is detectable in the keys of `globals()`, even if they are not passed in the `Bind` constructor.
  So we use the ordering of those elements to make an inference about which bindings to destroy.
- With args splatting we can naturally support binding multiple symbols `as` a tuple.
  This will only work as expected if you unpack the tuple in the `as` statement, however.
  The length check will go awry if you don't.

``` python
with Bind(1, 2, verbose=True) as bound_tuple:
    other_name = "some value"
## all new names: ['bound_tuple', 'other_name']
## bindings to clean: ['bound_tuple', 'other_name']
## deleting bound_tuple
## deleting other_name

# this shouldn't fail but it will bc we use one name for the len-2 tuple.
print(other_name)
## NameError: name 'other_name' is not defined
```

We could work around this with a flag that the user sets to indicate whether they unpack the tuple, but there's no way to enforce that behavior, so it isn't a great idea.
Well, none of this is a great idea, but you see what I mean.

If we had a way to detect which bindings specifically we create with the `as` statement, we could get it 100% right.[^2]

## Obligatory compliments to Julia

Julia has a way of always being sensible about stuff like this so we have scoped iterands and well-behaved `let` blocks.

``` julia
for i in 1:5
    x = i + 1
end

try
    print(i)
catch
    print("caught!")
end
## caught!
```

``` julia
let x = 1
    print(x)
end
## 1

try
    print(x)
catch
    print("caught")
end
## caught
```

[^1]: the `i` in `for i in ...`

[^2]: This is actually possible in some special cases. In a plain Python REPL you can inspect the stack frames and literally use the text of your code to identity which bindings are created by regex matching `with ... as ...`. This doesn't work in Quarto though because Quarto is smuggling the Python code around into strange execution contexts that I will not unwind for a blog post that doesn't pay the bills.
