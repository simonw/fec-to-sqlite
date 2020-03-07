import datetime


def save_filing(filing, db):
    d = {}
    d.update(
        {"header_{}".format(key): value for key, value in filing["header"].items()}
    )
    d.update(filing["filing"])
    stringify_datetimes(d)
    filing_id = db["filings"].insert(d, hash_id="id", alter=True, ignore=True).last_pk
    # Save the text and itemizations lists
    for items in filing["itemizations"].values():
        for item in items:
            item["filing_id"] = filing_id
            stringify_datetimes(item)
            db["itemizations"].insert(
                item,
                hash_id="id",
                alter=True,
                ignore=True,
                foreign_keys=[("filing_id", "filings", "id")],
            )
    for text in filing["text"]:
        text["filing_id"] = filing_id
        db["texts"].insert(
            text,
            hash_id="id",
            alter=True,
            ignore=True,
            foreign_keys=[("filing_id", "filings", "id")],
        )


def stringify_datetimes(d):
    for key, value in d.items():
        if isinstance(value, datetime.datetime):
            d[key] = str(value)
