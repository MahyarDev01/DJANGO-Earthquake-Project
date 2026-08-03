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
from Src.Other.helpers_func import haversine_distance

def plot_heatmap():
    engine = get_engine()
    df = pd.read_sql("SELECT latitude, longitude, magnitude FROM earthquakes;", engine)

    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    df['magnitude'] = pd.to_numeric(df['magnitude'], errors='coerce')
    df = df.dropna(subset=['latitude', 'longitude'])

    # محاسبه فاصله تا توکیو
    df['distance_to_tokyo'] = haversine_distance(df['latitude'], df['longitude'])

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # ۱. هیت‌مپ توزیع جغرافیایی (طول و عرض جغرافیایی)
    sns.kdeplot(
        data=df, x="longitude", y="latitude", cmap="Reds", fill=True,
        cbar=True, levels=15, ax=axes[0]
    )
    axes[0].set_title("Geographic Density Heatmap of Japan Earthquakes", fontsize=12, fontweight='bold')
    axes[0].set_xlabel("Longitude")
    axes[0].set_ylabel("Latitude")

    # ۲. هیت‌مپ فاصله تا توکیو در برابر بزرگی
    sns.kdeplot(
        data=df.dropna(subset=['magnitude']), x="distance_to_tokyo", y="magnitude",
        cmap="YlOrRd", fill=True, cbar=True, levels=15, ax=axes[1]
    )
    axes[1].set_title("Heatmap: Distance to Tokyo vs Magnitude", fontsize=12, fontweight='bold')
    axes[1].set_xlabel("Distance to Tokyo (km)")
    axes[1].set_ylabel("Magnitude (M)")

    plt.tight_layout()
    output_path = os.path.join(project_root, "Data", "heatmap_earthquakes.png")
    plt.savefig(output_path, dpi=300)
    print(f"✅ نقشه‌های حرارتی ذخیره شدند:\n📍 {output_path}")
    plt.show()

if __name__ == "__main__":
    plot_heatmap()