import os
import argparse
import pandas as pd
from tensorboard.backend.event_processing import event_accumulator


def find_event_files(log_dir):
    event_files = []
    for root, _, files in os.walk(log_dir):
        for f in files:
            if "tfevents" in f:
                event_files.append(os.path.join(root, f))
    return event_files


def load_events(event_file):
    ea = event_accumulator.EventAccumulator(
        event_file,
        size_guidance={
            event_accumulator.SCALARS: 0  # 读取全部数据
        }
    )
    ea.Reload()
    return ea


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_dir", type=str, required=True,
                        help="TensorBoard log directory")
    parser.add_argument("--output_dir", type=str, default=None,
                        help="Output CSV directory")
    args = parser.parse_args()

    log_dir = args.log_dir
    output_dir = args.output_dir or os.path.join(log_dir, "tb_csv")
    os.makedirs(output_dir, exist_ok=True)

    print(f"Scanning directory: {log_dir}")
    event_files = find_event_files(log_dir)

    if not event_files:
        print("No event files found.")
        return

    print(f"Found {len(event_files)} event file(s).")

    # 用于合并多个event文件
    scalar_data = {}

    for event_file in event_files:
        print(f"Loading: {event_file}")
        ea = load_events(event_file)

        for tag in ea.Tags()["scalars"]:
            events = ea.Scalars(tag)

            if tag not in scalar_data:
                scalar_data[tag] = []

            for e in events:
                scalar_data[tag].append({
                    "step": e.step,
                    "value": e.value,
                    "wall_time": e.wall_time
                })

    # 导出
    for tag, data in scalar_data.items():
        df = pd.DataFrame(data)

        # 按step排序
        df = df.sort_values(by="step")

        safe_tag = tag.replace("/", "_")
        csv_path = os.path.join(output_dir, f"{safe_tag}.csv")

        df.to_csv(csv_path, index=False)
        print(f"Exported: {csv_path}")

    print("\nAll scalars exported successfully.")


if __name__ == "__main__":
    main()