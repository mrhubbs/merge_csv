"""
10-20-15
"""


import tempfile
import csv


def load_csv_as_dict(csv_path):
    """
    Loads a CSV into a dictionary.
    """
    with open(csv_path, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        header_row = reader.next()
        dat = [[] for _ in header_row]
        row_len = len(header_row)

        for row in reader:
            row_idx = 0

            if len(row) < row_len:
                print("row too small, skipping")
                continue

            while row_idx < row_len:
                try:
                    val = float(row[row_idx])
                except (ValueError, SyntaxError):
                    val = str(row[row_idx])

                dat[row_idx].append(val)
                row_idx += 1

    return {h: d for h, d in zip(header_row, dat)}


def save_dict_as_csv(dat, csv_path):
    """
    Saves, in the CSV format, the data in the dict dat to the file
    specified by csv_path.
    """

    # Create a temporary csv file to write to.
    csv_temp = tempfile.TemporaryFile()
    writer = csv.writer(csv_temp, delimiter=',')
    # Write the header.
    writer.writerow(dat.keys())

    # Write the rest of the data.
    idx = 0
    the_data = dat.values()
    length = len(the_data[0])
    header_range = range(len(dat.keys()))
    while idx < length:
        # Build the row.
        row = [the_data[i][idx] for i in header_range]
        # Write the row.
        writer.writerow(row)

        idx += 1

    # Copy the temporary csv file to the actual file we should be outputting
    # to.  Not writing directly to our output file prevents us from corrupting
    # it if something goes wrong.
    copy_temp_file(csv_temp, csv_path)
    csv_temp.close()


def get_smallest_number_of_lines(d):
    lengths = [len(i) for i in d.values()]

    if len(lengths) < 1:
        return 0
    else:
        return min(lengths)


def truncate_dict(d, length):
    for key, value in d.items():
        d[key] = value[:length]

    return d


def merge_dicts_by_mappings(dicts, mappings):
    out = {}

    for dictkey, mappings in mappings.items():
        for _from, _to in mappings:
            out[_to] = dicts[dictkey][_from]

    return out


def copy_temp_file(temp_fd, fpath, bs=4096):
    """
    Copies all data written to temp_fd to the file specified by fpath.
    """
    temp_fd.seek(0)
    copy = open(fpath, 'w')
    dat = temp_fd.read(bs)
    while dat:
        copy.write(dat)
        dat = temp_fd.read(bs)

    copy.close()

