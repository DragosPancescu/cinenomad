import subprocess
import signal
import os


def open_flatpak_chrome(url: str, profile: str, *args) -> subprocess.Popen:
    """Opens a URL in Google Chrome installed via Flatpak with optional arguments.

    Args:
        url (str): The URL to open.
        profile (str): Chrome profile, either 'Default' or 'Profile 1', 'Profile 2', etc. for subsequent profiles.
        args: Chrome process accepted args
     Returns:
        subprocess.Popen: Chrome process spawned by this method
    """

    # Base command
    command = ["flatpak", "run", "com.google.Chrome"]

    # Add any additional arguments
    if args:
        command.extend(args)

    # Specify the user profile
    command.append(f"--profile-directory={profile}")

    # Append the URL
    command.append(url)
    print(command)

    try:
        # Run the command and return the process
        process = subprocess.Popen(command, preexec_fn=os.setpgrp)
        return process
    except FileNotFoundError:
        print("Flatpak is not installed, or Chrome is not installed via Flatpak.")
    except subprocess.CalledProcessError as exception:
        print(f"Failed to open Chrome via Flatpak: {exception}")
    except Exception as exception:
        print(f"An error occurred: {exception}")
    return None


def close_chrome(process: subprocess.Popen) -> None:
    """Closes the Chrome instance launched via Flatpak.

    Args:
        process (subprocess.Popen): The Popen process object for the Chrome instance.
    """
    if process:
        try:
            # Kill the entire process group using the PGID
            pgid = os.getpgid(process.pid)
            os.killpg(pgid, signal.SIGTERM)
            print("Chrome closed successfully.")
        except Exception as exception:
            print(f"An error occurred while closing Chrome: {exception}")
    else:
        print("No process found to terminate.")
