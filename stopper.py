import os
import argparse


def create_stopper_file(tester):
    stopper_file = f"{tester}-stopper.txt"
    if not os.path.exists(stopper_file):
        with open(stopper_file, "w") as file:
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create stopper file")
    parser.add_argument("--tester", required=True, help="Tester name")
    args = parser.parse_args()

    TESTER = args.tester
    TESTER = TESTER.strip().upper()

    create_stopper_file(TESTER)
