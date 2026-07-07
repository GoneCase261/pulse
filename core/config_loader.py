import json
import os

SPORTS_CONFIG_DIR = "sports_configs"


def load_sport_config(sport_name):
    config_path = os.path.join(SPORTS_CONFIG_DIR, f"{sport_name}.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}"
        )

    with open(config_path, 'r', encoding="utf-8") as f:
        config = json.load(f)

    config["target_classes"] = {
        int(k): v
        for k, v in config["target_classes"].items()
    }

    return config
