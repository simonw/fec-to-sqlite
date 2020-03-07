import click
import requests
import sqlite_utils
import tqdm
import fecfile
from .utils import save_filing, start_iter_http


@click.group()
@click.version_option()
def cli():
    "Save FEC campaign finance data to a SQLite database"


@cli.command()
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.argument("filing_ids", type=int, nargs=-1)
def filings(db_path, filing_ids):
    "Import specific filings from the FEC API"
    db = sqlite_utils.Database(db_path)
    for filing_id in filing_ids:
        fec_generator, total_bytes = start_iter_http(filing_id)
        with tqdm.tqdm(total=total_bytes, desc=str(filing_id)) as pbar:
            save_filing(fec_generator(callback=pbar.update), db)
    db.index_foreign_keys()
