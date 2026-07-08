import io
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from aiogram.types import BufferedInputFile


def build_weight_chart(history: list[dict]) -> BufferedInputFile:
    dates = []
    weights = []
    for row in history:
        raw = row["logged_at"]
        try:
            dt = datetime.strptime(raw[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            dt = datetime.fromisoformat(raw)
        dates.append(dt)
        weights.append(row["weight"])

    fig, ax = plt.subplots(figsize=(7, 4), dpi=150)
    ax.plot(dates, weights, marker="o", color="#2E86AB", linewidth=2)
    ax.fill_between(dates, weights, min(weights) - 1, color="#2E86AB", alpha=0.1)
    ax.set_title("Прогрес ваги", fontsize=14, fontweight="bold")
    ax.set_ylabel("Вага, кг")
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    return BufferedInputFile(buf.read(), filename="progress.png")
