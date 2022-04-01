import logging
import os
import sys
from pathlib import Path
from formulas import *
from prover import HonestProver
from verifier import run_verifier, VERIFIER_DEFAULT_SEED


def _resolve_root():
    base_path = Path(__file__).parent
    return (base_path / "../logs/").resolve()


def _configure_loggers():
    for log_module in ["protocol", "prover"]:

        fh = logging.FileHandler(os.path.join(_resolve_root(), "%s.log" % log_module), mode="w")
        fh.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(message)s")
        fh.setFormatter(formatter)

        logger = logging.getLogger(log_module)
        logger.setLevel(logging.DEBUG)

        logger.addHandler(fh)


def tqbfip(qbf: QBF, seed: int):

    _configure_loggers()

    logger = logging.getLogger("protocol")

    prover = HonestProver(qbf)

    logger.info("Working modulo prime p = %d", prover.p)

    prover.log_operator_polynomials()

    accepted = run_verifier(qbf, prover, prover.p, seed)

    logger.info("-" * 30)
    logger.info("[V]: Proof %s.", "accepted" if accepted else "rejected")


if __name__ == "__main__":

    qbf = default_example_formula()

    seed = int(sys.argv[1]) if len(sys.argv) >= 2 else VERIFIER_DEFAULT_SEED

    print("Seed: %d. Executing interactive protocol..." % seed)

    tqbfip(qbf, seed)

    print("Done!")
    print("The transcript of the protocol as well as other information can be found in the /logs/ directory.")
