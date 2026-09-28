import yaml


def load_config(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)