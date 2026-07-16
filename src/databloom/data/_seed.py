"""Deterministic seeds for reproducible data generation.

All dataset generators must import seeds from this module
to guarantee that datasets are bit-for-bit identical across runs.
"""

from databloom.settings import settings

# Master seed — do not change without regenerating all datasets
_MASTER_SEED = settings.data_gen.master_seed

# Per-dataset seeds, derived from the master seed.
# Each dataset gets its own seed block to avoid coupling between datasets.

SEEDS: dict[str, int] = {
    "finance_profit": _MASTER_SEED + 42,
    "finance_metrics": _MASTER_SEED + 43,
    "sales_orders": _MASTER_SEED + 100,
    "hr_workforce": _MASTER_SEED + 200,
    "supply_chain": _MASTER_SEED + 300,
}
