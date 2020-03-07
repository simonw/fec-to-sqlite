import click
import requests
import sqlite_utils
import tqdm
import fecfile
from .utils import save_filing


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
    for filing_id in tqdm.tqdm(filing_ids):
        save_filing(fecfile.from_http(filing_id), db)
