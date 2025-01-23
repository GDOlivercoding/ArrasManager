import os

print("Downloading requirements...")
did_error = os.system("py -m pip install -r requirements.txt")
if did_error:
    print(
        "Python is not installed"
        ", or cannot be accessed"
        "\nfailed command: py -m pip install -r requirements.txt"
        "\ncheck your internet connection and try again"
    )

input("Done!")
