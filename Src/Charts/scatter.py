
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(src_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from Src.Database.db_connection import get_engine

def plot_scatter():
    engine = get_engine()
    df = pd.read_sql("SELECT depth, magnitude, time FROM earthquakes;", engine)

    df['magnitude'] = pd.to_numeric(df['magnitude'], errors='coerce')
    df['depth'] = pd.to_numeric(df['depth'], errors='coerce')
    df['time'] = pd.to_datetime(df['time'], errors='coerce', utc=True)
    df = df.dropna(subset=['depth', 'magnitude'])

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    sns.set_theme(style="whitegrid")

    # ۱. عمق در برابر بزرگی
    sns.scatterplot(data=df, x="depth", y="magnitude", alpha=0.6, color="crimson", ax=axes[0])
    axes[0].set_title("Magnitude vs Depth", fontsize=13, fontweight='bold')
    axes[0].set_xlabel("Depth (km)")
    axes[0].set_ylabel("Magnitude (M)")

    # ۲. بزرگی در برابر زمان
    sns.scatterplot(data=df, x="time", y="magnitude", alpha=0.6, color="navy", ax=axes[1])
    axes[1].set_title("Magnitude vs Time", fontsize=13, fontweight='bold')
    axes[1].set_xlabel("Time")
    axes[1].set_ylabel("Magnitude (M)")

    plt.tight_layout()
    output_path = os.path.join(project_root, "Data", "scatter_magnitude.png")
    plt.savefig(output_path, dpi=300)
    print(f"✅ نمودار پراکندگی ذخیره شد:\n📍 {output_path}")
    plt.show()

if __name__ == "__main__":
    plot_scatter()