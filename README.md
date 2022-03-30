# TQBFIP

In complexity theory, it is well known that IP = PSPACE ([Shamir's Theorem](https://dl.acm.org/doi/10.1145/146585.146609)). Since IP is contained in PSPACE, it suffices to show that PSPACE is contained in IP, which is done by constructing an interactive proof for TQBF (IP is closed under polynomial-time Karp reductions). This project contains an implementation of the interactive proof protocol for TQBF presented in [Shamir's paper](https://dl.acm.org/doi/10.1145/146585.146609), with the use of the linearization operator discovered by Shen in [this paper](https://dl.acm.org/doi/10.1145/146585.146613).

Apart from the implementation of the protocol itself, this project contains a clean, detailed & generic renderer of a video animation for the entire protocol. The goal of this animation is to visualize how exactly everything works in the protocol, both before as well as during the communication.

## Installation & Usage

This project is intended to be used for educational purposes.

## Copyright

Copyright (c) 2022 Alexander Mayorov.

This project is licenced under the MIT License.

Please leave a license and copyright notice if you use or modify this software or parts of it.

See the `LICENSE` file for more details.