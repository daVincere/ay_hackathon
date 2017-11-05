import csv, json

def read_json(filename):
    return json.loads(open(filename).read())
def write_csv(data,filename):
    with open(filename) as outf:
        writer = csv.DictWriter(outf, data[0].keys())
        writer.writeheader()
        for row in data:
            writer.writerow(row)
# implement
write_csv(read_json('test.json'), 'output.csv')