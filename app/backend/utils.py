import os


def write_to_env_file(key: str, value: str):
    env_file_path = ".env"
    if os.path.exists(env_file_path):
        with open(env_file_path, "r") as env_file:
            lines = env_file.readlines()
        with open(env_file_path, "w") as env_file:
            for line in lines:
                if not line.startswith(f"{key}="):
                    env_file.write(line)
    with open(env_file_path, "a") as env_file:
        env_file.write(f"{key}={value}\n")
