"""Run only when the upstream real daily text file is available; never fabricate it."""
from src.models.run import main


if __name__ == '__main__':
    main(real=True)
