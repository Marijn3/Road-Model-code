import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

log_data = {"before": """
[2024-03-27 15:51:00,003] (INFO) road model -> load dataframes: Laag Wegvakken laden...
[2024-03-27 15:51:14,101] (INFO) road model -> load dataframes: Laag Rijstroken laden...
[2024-03-27 15:51:17,273] (INFO) road model -> load dataframes: Laag Kantstroken laden...
[2024-03-27 15:51:21,108] (INFO) road model -> load dataframes: Laag Mengstroken laden...
[2024-03-27 15:51:22,437] (INFO) road model -> load dataframes: Laag Maximum snelheid laden...
[2024-03-27 15:51:24,358] (INFO) road model -> load dataframes: Laag Convergenties laden...
[2024-03-27 15:51:24,832] (INFO) road model -> load dataframes: Laag Divergenties laden...
[2024-03-27 15:51:25,325] (INFO) road model -> load dataframes: Laag Rijstrooksignaleringen laden...
[2024-03-27 15:51:27,700] (INFO) road model ->  process dataframes: Laag 'Wegvakken' wordt geïmporteerd...
[2024-03-27 15:51:27,739] (INFO) road model ->  process dataframes: Laag 'Rijstroken' wordt geïmporteerd...
[2024-03-27 15:51:27,842] (INFO) road model ->  process dataframes: Laag 'Kantstroken' wordt geïmporteerd...
[2024-03-27 15:51:28,043] (INFO) road model ->  process dataframes: Laag 'Mengstroken' wordt geïmporteerd...
[2024-03-27 15:51:28,096] (INFO) road model ->  process dataframes: Laag 'Maximum snelheid' wordt geïmporteerd...
[2024-03-27 15:51:28,404] (INFO) road model ->  process dataframes: Laag 'Rijstrooksignaleringen' wordt geïmporteerd...
[2024-03-27 15:51:28,447] (INFO) road model ->  process dataframes: Laag 'Convergenties' wordt geïmporteerd...
[2024-03-27 15:51:28,450] (INFO) road model ->  process dataframes: Laag 'Divergenties' wordt geïmporteerd...
[2024-03-27 15:51:29,185] (INFO) msi relations -> construct msi network: MSI-netwerk opzetten...
[2024-03-27 15:51:29,332] (INFO) visualiser -> visualise roads: Sectiedata visualiseren...
[2024-03-27 15:51:29,501] (INFO) visualiser -> visualise msis: Puntdata visualiseren...
[2024-03-27 15:51:29,619] (INFO) visualiser -> visualise msis: MSI-relaties visualiseren...
[2024-03-27 15:51:30,087] (INFO) visualiser -> save image: Visualisatie succesvol afgerond.
""", "after": """
[2024-03-27 15:48:28,107] (INFO) road model -> load dataframes: Laag 'Wegvakken' laden...
[2024-03-27 15:48:28,606] (INFO) road model -> load dataframes: Laag 'Rijstroken' laden...
[2024-03-27 15:48:28,810] (INFO) road model -> load dataframes: Laag 'Kantstroken' laden...
[2024-03-27 15:48:29,113] (INFO) road model -> load dataframes: Laag 'Mengstroken' laden...
[2024-03-27 15:48:29,222] (INFO) road model -> load dataframes: Laag 'Maximum snelheid' laden...
[2024-03-27 15:48:29,372] (INFO) road model -> load dataframes: Laag 'Convergenties' laden...
[2024-03-27 15:48:29,426] (INFO) road model -> load dataframes: Laag 'Divergenties' laden...
[2024-03-27 15:48:29,485] (INFO) road model -> load dataframes: Laag 'Rijstrooksignaleringen' laden...
[2024-03-27 15:48:29,720] (INFO) road model ->  process dataframes: Laag 'Wegvakken' wordt verwerkt in het wegmodel...
[2024-03-27 15:48:29,733] (INFO) road model ->  process dataframes: Laag 'Rijstroken' wordt verwerkt in het wegmodel...
[2024-03-27 15:48:29,835] (INFO) road model ->  process dataframes: Laag 'Kantstroken' wordt verwerkt in het wegmodel...
[2024-03-27 15:48:30,034] (INFO) road model ->  process dataframes: Laag 'Mengstroken' wordt verwerkt in het wegmodel...
[2024-03-27 15:48:30,084] (INFO) road model ->  process dataframes: Laag 'Maximum snelheid' wordt verwerkt in het wegmodel...
[2024-03-27 15:48:30,395] (INFO) road model ->  process dataframes: Laag 'Rijstrooksignaleringen' wordt verwerkt in het wegmodel...
[2024-03-27 15:48:30,437] (INFO) road model ->  process dataframes: Laag 'Convergenties' wordt verwerkt in het wegmodel...
[2024-03-27 15:48:30,441] (INFO) road model ->  process dataframes: Laag 'Divergenties' wordt verwerkt in het wegmodel...
[2024-03-27 15:48:31,191] (INFO) msi relations -> construct msi network: MSI-netwerk opzetten...
[2024-03-27 15:48:31,351] (INFO) visualiser -> visualise roads: Sectiedata visualiseren...
[2024-03-27 15:48:31,499] (INFO) visualiser -> visualise msis: Puntdata visualiseren...
[2024-03-27 15:48:31,664] (INFO) visualiser -> visualise msis: MSI-relaties visualiseren...
[2024-03-27 15:48:32,110] (INFO) visualiser -> save image: Visualisatie succesvol afgerond.
"""}

fig, axs = plt.subplots(2, 1, figsize=(10, 4.7), sharex=True)


for i, (name, data) in enumerate(log_data.items()):
    # Parse timestamps and calculate durations
    start_time = None
    previous_step = None
    durations = {}
    steps = []

    for log in data.split("\n"):
        if log.strip():
            timestamp_str = log[1:24]  # Extract timestamp string
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f")

            if start_time is None:
                start_time = timestamp

            duration = (timestamp - start_time).total_seconds()

            step = log.split("->")[1].split(":")[0].strip()
            step = step.split('laden')[0].split('wordt')[0].strip()  # Clean up step names

            if step == previous_step or not previous_step:
                if step in durations:
                    durations[step] += duration
                else:
                    durations[step] = duration
            else:
                if previous_step in durations:
                    durations[previous_step] += duration
                else:
                    durations[previous_step] = duration

            previous_step = step

            start_time = timestamp

    # Convert durations to weight counts
    weight_counts = {}
    for step, duration in durations.items():
        weight_counts[step] = np.array([duration])

    # Plot bars
    bottom = 0
    for step, weight_count in weight_counts.items():
        axs[i].barh(f"Timeline {name}", weight_count, 0.4, label=step, left=bottom)
        bottom += weight_count

    if i == 0:
        axs[i].set_title(f"Timelines before and after change", weight='bold', size=16)
    axs[i].tick_params(axis='both', which='major', labelsize=14)

plt.legend(loc="lower right", fontsize=14)

plt.xlabel('Duration (seconds)', size=14)

# Invert y-axis for both timelines
for ax in axs:
    ax.invert_yaxis()

plt.tight_layout()
plt.savefig('timeline_plot.pdf', format='pdf')
plt.show()
