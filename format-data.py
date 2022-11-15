import csv

with open("stat_data.txt") as data:
    with open("marisa_history.csv", "w") as file:
        split_on_dash = []

        writer = csv.writer(file)

        for line in data:
            split_on_dash.append(line.split("-"))
            # print(f"{line.split('-')}")

        for row in split_on_dash:
            date = row[0]
            datas = row[1].split("/")
            if len(datas) > 1:
                for each in datas:
                    a = [date, each.strip("\n")]
                    writer.writerow(a)
            else:
                a = [date, datas[0].strip("\n")]
                writer.writerow(a)
