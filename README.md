# TQBFIP

In complexity theory, it is well known that IP = PSPACE ([Shamir's Theorem](https://dl.acm.org/doi/10.1145/146585.146609)). It is not hard to see why IP is contained in PSPACE, so it suffices to show that PSPACE is contained in IP, which is done by constructing an interactive proof for TQBF (IP is closed under polynomial-time Karp reductions). This project contains an implementation of the interactive proof protocol for TQBF presented in [Shamir's paper](https://dl.acm.org/doi/10.1145/146585.146609), with the use of the linearization operator discovered by Shen in [this paper](https://dl.acm.org/doi/10.1145/146585.146613). For example, this project can be used to obtain a concrete interactive transcript of the communication between the prover and the verifier (see below for more details).

Apart from the implementation of the protocol itself, this project contains a clean, detailed & generic renderer of a video animation for the entire protocol. The goal of this animation is to visualize how exactly everything works in the protocol, both before as well as during the communication. Concretely, the following stages are animated:

* Arithmetization, that is, the conversion of the QBF sentence into a polynomial
* Communication between the prover and the verifier, that is, how the prover shows the truth of the QBF sentence and how the verifier checks that the proof presented is indeed correct.

## Installation

**Python version**: 3.9.5 or newer

**Python dependencies** to be installed:

* [SymPy](https://www.sympy.org/) 1.10.1 or newer
* [Manim Community Edition](https://www.manim.community/) v0.15.1 or newer

**Note**: The latter library is used only for the animation rendering, you don't need to install `manim` if you don't want to render animations.

## Usage

This project is intended to be used for educational purposes. TBA

## Copyright

Copyright (c) 2022 Alexander Mayorov.

This project is licenced under the MIT License.

Please leave a license and copyright notice if you use or modify this software or parts of it.

See the `LICENSE` file for more details.