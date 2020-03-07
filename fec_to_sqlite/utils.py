import datetime
import fecfile
from fecfile import fecparser
import requests


def save_filing(filing_generator, db):
    filing = {}
    filing_id = None
    for i, fecitem in enumerate(filing_generator):
        # First gather the header and summary
        if i == 0:
            assert fecitem.data_type == "header"
            filing.update(
                {"header_{}".format(key): value for key, value in fecitem.data.items()}
            )
            continue
        if i == 1:
            assert fecitem.data_type == "summary"
            filing.update(fecitem.data)
            stringify_datetimes(filing)
            with db.conn:
                filing_id = (
                    db["filings"]
                    .insert(filing, hash_id="id", alter=True, ignore=True)
                    .last_pk
                )
            continue
        assert fecitem.data_type in ("itemization", "text", "F99_text")
        if fecitem.data_type == "itemization":
            item = fecitem.data
            item["filing_id"] = filing_id
            stringify_datetimes(item)
            with db.conn:
                db["itemizations"].insert(
                    item,
                    hash_id="id",
                    alter=True,
                    ignore=True,
                    foreign_keys=[("filing_id", "filings", "id")],
                )
            continue
        if fecitem.data_type == "text":
            text = fecitem.data
            text["filing_id"] = filing_id
            with db.conn:
                db["texts"].insert(
                    text,
                    hash_id="id",
                    alter=True,
                    ignore=True,
                    foreign_keys=[("filing_id", "filings", "id")],
                )
            continue
        # Don't know what to do with this, print it out
        print("Unknown type: {}".format(fecitem.data_type))
        print("  ", fecitem.data)


def stringify_datetimes(d):
    for key, value in d.items():
        if isinstance(value, datetime.datetime):
            d[key] = str(value)


def start_iter_http(filing_id, options=None):
    options = options or {}
    url = "https://docquery.fec.gov/dcdev/posted/{n}.fec".format(n=filing_id)
    req_headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=req_headers, stream=True)

    def fec_generator(callback=lambda x: None):
        nonlocal r

        def iter_lines():
            for line in r.iter_lines():
                yield line
                callback(len(line))

        if r.status_code == 404:
            url = "https://docquery.fec.gov/paper/posted/{n}.fec".format(n=filing_id)
            r = requests.get(url, headers=req_headers, stream=True)
        if r.status_code == 200:
            for item in fecparser.iter_lines(iter_lines(), options=options):
                yield item
        else:
            raise fecfile.FilingUnavailableError({"file_number": filing_id})

    return fec_generator, int(r.headers["content-length"])
