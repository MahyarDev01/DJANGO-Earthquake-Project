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

def plot_boxplot():
    engine = get_engine()
    df = pd.read_sql("SELECT depth, magnitude FROM earthquakes;", engine)

    df['magnitude'] = pd.to_numeric(df['magnitude'], errors='coerce')
    df['depth'] = pd.to_numeric(df['depth'], errors='coerce')
    df = df.dropna(subset=['depth', 'magnitude'])

    # گروه‌بندی عمق زلزله
    bins = [0, 30, 70, 300, 1000]
    labels = ['Shallow (<30km)', 'Intermediate (30-70km)', 'Deep (70-300km)', 'Very Deep (>300km)']
    df['depth_group'] = pd.cut(df['depth'], bins=bins, labels=labels)

    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x="depth_group", y="magnitude", palette="Set3")
    plt.title("Magnitude Distribution Across Depth Categories", fontsize=13, fontweight='bold')
    plt.xlabel("Depth Category")
    plt.ylabel("Magnitude (M)")

    plt.tight_layout()
    output_path = os.path.join(project_root, "Data", "boxplot_depth_mag.png")
    plt.savefig(output_path, dpi=300)
    print(f"✅ نمودار جعبه‌ای ذخیره شد:\n📍 {output_path}")
    plt.show()

if __name__ == "__main__":
    plot_boxplot()