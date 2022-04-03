# TQBFIP

In complexity theory, it is well known that IP = PSPACE ([Shamir's Theorem](https://dl.acm.org/doi/10.1145/146585.146609)). It is not hard to see why IP is contained in PSPACE, so it suffices to show that PSPACE is contained in IP, which is done by constructing an interactive proof for TQBF (IP is closed under polynomial-time Karp reductions). This project contains an implementation of the above mentioned interactive proof protocol for TQBF presented in [Shamir's paper](https://dl.acm.org/doi/10.1145/146585.146609), with the use of the linearization operator introduced by Shen in [this paper](https://dl.acm.org/doi/10.1145/146585.146613). For example, this project can be used to obtain a concrete interactive transcript of the communication between the prover and the verifier (see below for more details).

Apart from the implementation of the protocol itself, this project contains a clean, detailed & generic renderer of a video animation for the entire protocol. The goal of this animation is to visualize how exactly everything works in the protocol, both before as well as during the communication. Concretely, the following stages are animated:

* Arithmetization, that is, the conversion of the QBF matrix into a polynomial
* Communication between the prover and the verifier, that is, how the prover shows the validity of the QBF sentence and how the verifier interactively checks that the proof being presented is indeed correct.

Overall, this project is intended to be used for educational purposes. See [this blog post](https://zerobone.net/blog/cs/ip-pspace/) for a clear description of the protocol, the visualizations generated using this project, the relevant notation and details.

## Installation

**Python version**: 3.9.5 or newer

**Required python dependencies**:

* [NumPy](https://numpy.org/) v1.19 or newer
* [SymPy](https://www.sympy.org/) 1.10.1 or newer
* [Manim CE](https://www.manim.community/) v0.15.1 or newer

For the installation of the above libraries, make sure you follow the official guide available on the corresponding website. The Manim CE library is used only for the animation rendering, you don't have to install it if you are not planning to render animations.

## Usage

To execute the interactive protocol, run

```shell
python tqbfip.py [seed]
```

in the `src` directory. Here, by replacing `[seed]` with some integer, it is possible to adjust the verifier's random number generator seed. This is useful when we want to execute the protocol multiple times without having the numbers the verifier chooses at random change every time. In case this parameter is omitted, a default hardcoded seed will be used.

By default, the protocol will be executed for the formula generated by `default_example_formula()` in `src/formulas.py`. To execute the protocol for a custom QBF sentence, construct it using the `QBF` class and pass it as an argument to `tqbfip(qbf, seed)`. You can find examples of formulas and the way they can be constructed in `src/formulas.py`. Please note that the `QBF` class supports only formulas already in prenex normal form with matrix in CNF. If this is not the case for your formula, first convert it into NNF, then bring quantifiers out and finally apply Tseitin's transformation to ensure that the matrix is in CNF.

Once the protocol execution has finished, you will find the interactive transcript of the communication in `logs/protocol.log`. More advanced prover-related information, such as the list of composed operator polynomials, is written to `logs/prover.log`.

### Animating arithmetization

To render the animation showing how the QBF matrix is arithmetized, run

```shell
python anim_arithmetization.py
```

from the `src` directory. This will render the animation in Full HD using default `manim` rendering options. Alternatively, you can render the animation by calling `manim` directly, that is, with the

```shell
manim -pql anim_arithmetization.py
```

command. Here, `-pql` stands for **p**lay, after rendering in **q**uality **l**ow mode. If you don't want the animation to be automatically played once rendering is complete, remove **p**. The rendering quality can be also changed from **l**ow to **m**edium or **h**igh. For more information regarding the `manim` command, see the official [Manim CE documentation](https://docs.manim.community/en/stable/).

The resulting animation will build the arithmetizing polynomial step-by-step resulting in, for example,

![Screenshot from the arithmetization animation](screenshots/arithmetization.jpg)

at the end of the video. You can view the complete arithmetization animation produced for this formula [on YouTube here](https://youtu.be/ZIR87YmcLME).

### Animating the interactive proof

Analogously to the above commands, the interactive proof can be animated by running

```shell
python anim_protocol.py
```

or, alternatively,

```shell
manim -pql anim_protocol.py
```

in the `src` directory. Rendering this animation will take considerably more time compared to the arithmetization animation discussed above. If you only need to animate a few first rounds, you can specify the amount of rounds to be animated via the `rounds_limit` parameter in the `ProtocolScene` constructor (`anim_protocol.py` module). If this parameter is set to `0` which is the default value, all interactive rounds will be animated.

Here are some screenshots from the animation that gets produced for the above example formula:

![Screenshot from the arithmetization animation](screenshots/protocol_01.jpg)

![Screenshot from the arithmetization animation](screenshots/protocol_02.jpg)

![Screenshot from the arithmetization animation](screenshots/protocol_03.jpg)

![Screenshot from the arithmetization animation](screenshots/protocol_04.jpg)

The entire animation is available [on YouTube](https://youtu.be/gSWT3DOiQtk).

**Note**: [This post](https://zerobone.net/blog/cs/ip-pspace/) contains both all the formal notation used in the visualization as well as a description of what each part of the animation means.

**Warning**: It is not recommended to animate arithmetization or the interactive proof when the QBF sentence contains more than 4 variables or clauses. The reason is that all parts of the animation may simply no longer fit on the screen.

## Copyright

Copyright (c) 2022 Alexander Mayorov.

This project is licensed under the MIT License. Please leave a license and copyright notice if you use this software. See the `LICENSE` file for more details.
