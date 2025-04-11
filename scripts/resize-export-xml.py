import subprocess

directory = "/Users/rod/PycharmProjects/FabricRoom/media/processed/Rod/HeartRate.csv"

with open(directory, 'r') as fp:
    lines = len(fp.readlines())

    print(lines)
    print(lines//2)

    if int(lines) % 2 != 0:
        print('fuck')
    else:
        print (lines//2)
 #   subprocess.run(["head", f"-{lines//2}", f"{directory}", ">", f"HeartRate1-{lines}"], capture_output=True)