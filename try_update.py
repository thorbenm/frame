import subprocess


def run_update_script():
    try:
        completed_process = subprocess.run(
            ["python", "/home/frame/Programming/frame/update.py"],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip()
        print(error_message)
        from _waveshare import show_text
        show_text(error_message)


if __name__ == "__main__":
    run_update_script()

