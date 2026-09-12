"""
Project configuration and credential loading.

Everything that used to be implicit under yfinance has to become explicit under
Polygon. All applicable default values and Polygon credential logic lives here.
"""

from typing import Optional

# ----------------------------------------------------------------------
# Numeric defaults
# ----------------------------------------------------------------------

#  Risk-free rate uses 4% as a hard-coded value in line with the 3-month Treasury
#  bill rate. Dealing with daily-horizon VaR on short-dated contracts the rate is 
#  a neglible factor.
DEFAULT_RISK_FREE_RATE = 0.04

# Matching years_to_expiry in src/options.py.
DAY_COUNT = 365.0

# Shares per option contract.
CONTRACT_MULTIPLIER = 100

DEFAULT_CONFIDENCE_LEVEL = 0.95

# Polygon free tier allowance.
FREE_TIER_REQUESTS_PER_MINUTE = 5

# Name of the environment variable holding the Polygon key.
POLYGON_KEY_VAR = "POLYGON_API_KEY"


# ----------------------------------------------------------------------
# Credentials
# ----------------------------------------------------------------------


class MissingAPIKeyError(RuntimeError):
    """
    Raised when POLYGON_API_KEY is not set.
    """


def load_environment(dotenv_path: Optional[str] = None) -> None:
    """
    Load the project `.env` into the process environment.

    Idempotent: safe to call more than once. Existing environment variables win
    over `.env` values, so an exported key can override the file without
    editing it.

    Parameters
    ----------
    dotenv_path : explicit path to the .env file. When None, search upward from
        the project root, which is what lets `streamlit run gui/app.py` and
        `pytest` from the root both find the same file.
    """
    raise NotImplementedError("load_environment is not implemented yet")


def get_api_key() -> str:
    """
    Return the Polygon API key, raising a clear error when it is missing.

    Raises rather than returning None on purpose. A missing key is a setup
    problem with a known fix (create `.env`, add POLYGON_API_KEY), and the
    failure should say that at the point of the mistake.

    Raises
    ------
    MissingAPIKeyError : when POLYGON_API_KEY is unset or empty.
    """
    raise NotImplementedError("get_api_key is not implemented yet")


def has_api_key() -> bool:
    """
    True when a Polygon key is available, without raising.
    Useful for the GUI, which should be able to show a friendly setup prompt instead
    of an exception traceback when the key has not been configured.
    """
    raise NotImplementedError("has_api_key is not implemented yet")
