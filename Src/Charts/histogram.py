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

def plot_magnitude_histogram():
    print("🔄 در حال دریافت داده‌ها از پایگاه داده...")
    engine = get_engine()
    
    query = "SELECT magnitude, source, place FROM earthquakes;"
    df = pd.read_sql(query, engine)

    df['magnitude'] = pd.to_numeric(df['magnitude'], errors='coerce')
    df = df.dropna(subset=['magnitude'])

    if df.empty:
        print("❌ هیچ داده معتبری یافت نشد.")
        return

    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    sns.histplot(
        data=df, x="magnitude", hue="source", element="step",
        stat="density", common_norm=False, bins=20, palette="Set2", ax=axes[0]
    )
    axes[0].set_title("Earthquake Magnitude Distribution by Source", fontsize=13, fontweight='bold')
    axes[0].set_xlabel("Magnitude (M)")
    axes[0].set_ylabel("Density")

    top_regions = df['place'].value_counts().head(5).index
    df_top = df[df['place'].isin(top_regions)]

    sns.histplot(
        data=df_top, x="magnitude", hue="place", element="step",
        stat="density", common_norm=False, bins=20, palette="tab10", ax=axes[1]
    )
    axes[1].set_title("Magnitude Distribution in Top 5 Regions", fontsize=13, fontweight='bold')
    axes[1].set_xlabel("Magnitude (M)")
    axes[1].set_ylabel("Density")

    plt.tight_layout()
    output_path = os.path.join(project_root, "Data", "histogram_magnitude.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✅ نمودار هیستوگرام در مسیر زیر ذخیره شد:\n📍 {output_path}")
    plt.show()

if __name__ == "__main__":
    plot_magnitude_histogram()
