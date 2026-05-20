"""NightShift version metadata."""

from __future__ import annotations


PACKAGE_VERSION = "0.2.4"
RELEASE_CHANNEL = "alpha"
hotdog_version = "bratwurst"
topping_version = "relish"

HOTDOG_VERSIONS = (
    "bratwurst",
    "italian-sausage",
    "footlong",
    "new-york",
    "chicago",
    "coney",
    "corn-dog",
    "kielbasa",
    "vienna",
    "andouille",
    "chorizo",
    "frankfurter",
)

TOPPING_VERSIONS = (
    "relish",
    "mustard",
    "mayo",
    "onions",
    "sauerkraut",
    "jalapenos",
    "pickles",
    "chili",
    "cheese",
    "sport-peppers",
    "ketchup",
    "slaw",
)


def display_version() -> str:
    return f"{PACKAGE_VERSION}-{RELEASE_CHANNEL}-{hotdog_version}-{topping_version}"


__version__ = PACKAGE_VERSION
