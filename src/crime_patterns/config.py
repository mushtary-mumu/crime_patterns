#%%
"""All the general configuration of the project."""
from pathlib import Path

#%%
SRC = Path(__file__).parent.resolve()
BLD = SRC.joinpath("..", "..", "bld").resolve()

TEST_DIR = SRC.joinpath("..", "..", "tests").resolve()
PAPER_DIR = SRC.joinpath("..", "..", "paper").resolve()

GROUPS = ["marital_status", "qualification"]

# Setting default CRS to OSGB36 / British National Grid
CRS = "EPSG:27700"

__all__ = ["BLD", "SRC", "TEST_DIR", "GROUPS", "CRS"]

# %%

# %%
