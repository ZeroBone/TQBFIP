import logging
import os
from pathlib import Path
from formulas import *
from prover import HonestProver
from verifier import run_verifier


def _resolve_root():
    base_path = Path(__file__).parent
    return (base_path / "../").resolve()


def main():

    qbf = example_2_formula()

    p = qbf.compute_prime_for_protocol()

    prover = HonestProver(qbf, p)

    fh = logging.FileHandler(os.path.join(_resolve_root(), "verifier.log"))
    fh.setLevel(logging.DEBUG)

    formatter = logging.Formatter("[%(levelname)7s]: %(message)s")
    fh.setFormatter(formatter)

    logger = logging.getLogger("tqbf_protocol")
    logger.setLevel(logging.DEBUG)

    logger.addHandler(fh)

    logger.info("Working modulo prime p = %d", p)

    accepted = run_verifier(qbf, prover, p, 0xcafe)

    logger.info("Verifier: %s", "accepts" if accepted else "rejects")


if __name__ == "__main__":
    main()
