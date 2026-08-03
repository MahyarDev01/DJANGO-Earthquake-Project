
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

def plot_line_chart():
    engine = get_engine()
    df = pd.read_sql("SELECT time, magnitude FROM earthquakes;", engine)

    df['magnitude'] = pd.to_numeric(df['magnitude'], errors='coerce')
    df['time'] = pd.to_datetime(df['time'], errors='coerce', utc=True)
    df = df.dropna(subset=['time', 'magnitude'])

    df.set_index('time', inplace=True)
    daily_stats = df.resample('D').agg(count=('magnitude', 'count'), mean_mag=('magnitude', 'mean')).reset_index()

    sns.set_theme(style="whitegrid")
    fig, ax1 = plt.subplots(figsize=(14, 6))

    color = 'tab:blue'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Earthquake Count', color=color)
    ax1.plot(daily_stats['time'], daily_stats['count'], color=color, marker='o', linewidth=2, label='Count')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Average Magnitude (M)', color=color)
    ax2.plot(daily_stats['time'], daily_stats['mean_mag'], color=color, linestyle='--', marker='s', linewidth=2, label='Avg Magnitude')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title("Daily Earthquake Count and Average Magnitude Trend", fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output_path = os.path.join(project_root, "Data", "linechart_trend.png")
    plt.savefig(output_path, dpi=300)
    print(f"✅ نمودار خطی ذخیره شد:\n📍 {output_path}")
    plt.show()

if __name__ == "__main__":
    plot_line_chart()
