"""
I/O-driven server

When it comes to server implementation, we can divide it into two parts:
1. I/O, Network, local disk ...
2. Logic, how to reply to a request.

Server becomes meaningful only if it can have some side effects:
game user get level up, create an account in a system, post a blog on a site ...
all of which will use I/O.

That's interesting, we often implement our server with I/O and logic bounded to each other:
accept user's request, and process it and save some data to database and return response to user through network.

When there is only one synchronous execution model, that's OK, but when we want to execute the same logic in
an asynchronous execution model, we must reimplement the logic in an asynchronous way, which the main difference is
brought by the I/O difference between synchronous I/O and asynchronous I/O.

So, if we could implement our logic that can run both in synchronous and asynchronous I/O, it will be greate,
it requires some type of I/O-driven execution framework that can wipe out the difference between different I/O model.

In the Python programming language, there is a concept called generator, which can be treated as an execution routine,
and it can communicate with the caller with the yield keyword, it can send data to the caller, and it can receive data
from the caller. The caller get chances to affect the inner-state of generator.

We can use the generator to implement I/O-driven framework, which the real I/O happens at the framework level and the
generator will just send I/O context information to the caller and the caller will do the real I/O
and send the I/O result to the generator to push the generator to the next step.
"""
