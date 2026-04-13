"""
plot_results.py
Heart Sleeve — Quick plot of any saved CSV from tests/data/

Usage:
    python plot_results.py                      # plots the most recent CSV
    python plot_results.py pressure_step_*.csv  # plots a specific file
    python plot_results.py --list               # list available data files
"""

import sys
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = Path(__file__).parent.parent / "data"

COLUMNS_PRESSURE = ["s1_kPa", "s2_kPa"]
COLUMN_X         = "time_ms"


def list_files():
    files = sorted(DATA_DIR.glob("*.csv"))
    if not files:
        print(f"No CSV files found in {DATA_DIR}")
        return
    print(f"Files in {DATA_DIR}:")
    for f in files:
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name:<50s}  {size_kb:.1f} KB")


def plot_file(path: Path):
    df = pd.read_csv(path)
    print(f"Loaded: {path.name}  ({len(df)} rows, columns: {list(df.columns)})")

    pressure_cols = [c for c in COLUMNS_PRESSURE if c in df.columns]
    if not pressure_cols:
        print("No recognised pressure columns found. Plotting all numeric columns.")
        pressure_cols = df.select_dtypes("number").columns.tolist()
        if COLUMN_X in pressure_cols:
            pressure_cols.remove(COLUMN_X)

    # Split by label if present
    if "label" in df.columns:
        groups = df["label"].unique()
    else:
        groups = [None]

    fig, axes = plt.subplots(len(pressure_cols), 1, figsize=(12, 4 * len(pressure_cols)), sharex=True)
    if len(pressure_cols) == 1:
        axes = [axes]

    for ax, col in zip(axes, pressure_cols):
        for grp in groups:
            subset = df[df["label"] == grp] if grp is not None else df
            label = str(grp) if grp is not None else col
            ax.plot(subset[COLUMN_X], subset[col], label=label, linewidth=0.9)
        ax.set_ylabel(col)
        ax.grid(True, alpha=0.4)
        if grp is not None:
            ax.legend(fontsize=8)

    axes[-1].set_xlabel("Time (ms)")
    plt.suptitle(path.stem)
    plt.tight_layout()
    plt.show()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", help="CSV filename(s) in tests/data/")
    parser.add_argument("--list", action="store_true", help="List available files")
    args = parser.parse_args()

    if args.list:
        list_files()
        return

    if args.files:
        paths = [DATA_DIR / f for f in args.files]
    else:
        # Default: most recently modified CSV
        candidates = sorted(DATA_DIR.glob("*.csv"), key=lambda p: p.stat().st_mtime)
        if not candidates:
            print(f"No CSV files found in {DATA_DIR}")
            return
        paths = [candidates[-1]]
        print(f"Plotting most recent file: {paths[0].name}")

    for path in paths:
        if not path.exists():
            print(f"File not found: {path}")
            continue
        plot_file(path)


if __name__ == "__main__":
    main()
