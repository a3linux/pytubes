import pytest
import numpy.random
import random
import tubes

def rand_chars():
    n_bytes = random.randint(0,10)
    # return ''.join(random.sample(string.ascii_letters, n_bytes))
    return numpy.random.bytes(n_bytes).decode("latin1")

def csv_escape(data):
    data = data.replace(b'"', b'""')
    return b'"' + data + b'"'


@pytest.mark.parametrize("seed", [random.getrandbits(64) for i in range(50)])
def test_fuzz_csv(seed):
    random.seed(seed)
    n_rows = random.randint(0, 30)
    n_cols = random.randint(0, 30)
    cols_to_read = random.sample(range(0, 30), random.randrange(30))
    csv_rows = []
    expected_rows = []
    for _ in range(n_rows):
        csv_row = []
        expected_row = (['xx'] * len(cols_to_read))
        for col_no in range(n_cols):
            data = rand_chars()
            if col_no in cols_to_read:
                expected_row[cols_to_read.index(col_no)] = data
            data = data.encode("utf8")
            if b'"' in data or b'\n' in data or b',' in data or random.choice([False, False, True]):
                data = csv_escape(data)
            csv_row.append(data)
        if len(csv_row) == 0:
            if 0 in cols_to_read:
                expected_row[cols_to_read.index(0)] = ''
        expected_rows.append(tuple(expected_row))
        csv_rows.append(b",".join(csv_row))
    slot_tube = tubes.Each(csv_rows).csv(headers=False).multi(lambda x: [x.get(c, 'xx').to(str) for c in cols_to_read])
    actual_rows = list(slot_tube)
    for row_num in range(len(expected_rows)):
        for col_num in range(len(cols_to_read)):
            expected = expected_rows[row_num][col_num]
            if len(cols_to_read) == 1:
                actual = actual_rows[row_num]
            else:
                actual = actual_rows[row_num][col_num]
            assert expected == actual
    assert len(expected_rows) == len(actual_rows)


@pytest.mark.parametrize("seed", [random.getrandbits(64) for i in range(50)])
def test_fuzz_tsv(seed):
    random.seed(seed)
    n_rows = random.randint(0, 30)
    n_cols = random.randint(0, 30)
    cols_to_read = random.sample(range(0, 30), random.randrange(30))
    tsv_rows = []
    expected_rows = []
    for _ in range(n_rows):
        tsv_row = []
        expected_row = (['xx'] * len(cols_to_read))
        for col_no in range(n_cols):
            data = '\t'
            while '\t' in data:
                data = rand_chars()
            if col_no in cols_to_read:
                expected_row[cols_to_read.index(col_no)] = data
            data = data.encode("utf8")
            tsv_row.append(data)
        if len(tsv_row) == 0:
            if 0 in cols_to_read:
                expected_row[cols_to_read.index(0)] = ''
        expected_rows.append(tuple(expected_row))
        tsv_rows.append(b'\t'.join(tsv_row))
    slot_tube = tubes.Each(tsv_rows).tsv(headers=False).multi(lambda x: [x.get(c, 'xx').to(str) for c in cols_to_read])
    actual_rows = list(slot_tube)
    for row_num in range(len(expected_rows)):
        for col_num in range(len(cols_to_read)):
            expected = expected_rows[row_num][col_num]
            if len(cols_to_read) == 1:
                actual = actual_rows[row_num]
            else:
                actual = actual_rows[row_num][col_num]
            assert expected == actual
    assert len(expected_rows) == len(actual_rows)