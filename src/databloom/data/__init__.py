"""Built-in datasets for databloom examples and reports.

Each dataset is generated once on first access and cached as a
pickle file in the ``datasets/`` directory. Subsequent loads
return the cached data, guaranteeing deterministic results.

Usage::

    from databloom.data import load_dataset, list_datasets

    # List available datasets
    print(list_datasets())

    # Load a dataset
    df = load_dataset("hr_workforce")        # returns DataFrame

    # Force regeneration
    df = load_dataset("hr_workforce", force_rebuild=True)
"""

from databloom.data._generators import list_datasets, load_dataset

__all__ = ["load_dataset", "list_datasets"]
