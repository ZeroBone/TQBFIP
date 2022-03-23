import logging
import os
from pathlib import Path
from formulas import *
from prover import HonestProver
from verifier import run_verifier


def _resolve_root():
    base_path = Path(__file__).parent
    return (base_path / "../logs/").resolve()


def _configure_loggers():
    for log_module in ["protocol", "prover"]:

        fh = logging.FileHandler(os.path.join(_resolve_root(), "%s.log" % log_module))
        fh.setLevel(logging.DEBUG)

        formatter = logging.Formatter("[%(levelname)7s]: %(message)s")
        fh.setFormatter(formatter)

        logger = logging.getLogger(log_module)
        logger.setLevel(logging.DEBUG)

        logger.addHandler(fh)


def main():

    _configure_loggers()

    qbf = example_2_formula()

    p = qbf.compute_prime_for_protocol()

    logger = logging.getLogger("protocol")

    logger.info("Working modulo prime p = %d", p)

    prover = HonestProver(qbf, p)

    accepted = run_verifier(qbf, prover, p, 0xcafe)

    logger.info("Verifier: %s", "accepts" if accepted else "rejects")


if __name__ == "__main__":
    main()
