"""Download Eurostat datasets and turn their wide TSV files into one row per value.

Eurostat TSV cells hold a number, a flag, or both, for example "76.02 b" or ": u".
A ":" means no value. Flags used in this project's data include:
    b  break in the time series (methodology changed, so values before and after don't compare directly)
    e  estimated
    u  low reliability
"""
import json
import urllib.request
from datetime import date
from pathlib import Path

DATA_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/{code}?format=TSV&compressed=false"
CODELIST_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/{name}/latest?format=TSV&lang=en"
DATASET_PAGE = "https://ec.europa.eu/eurostat/databrowser/view/{code}/default/table"


def download(code, raw_dir):
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"{code}.tsv"
    urllib.request.urlretrieve(DATA_URL.format(code=code), path)
    return path


def download_codelist(name, raw_dir):
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"codelist_{name}.tsv"
    urllib.request.urlretrieve(CODELIST_URL.format(name=name), path)
    return path


def write_manifest(codes, raw_dir, accessed=None):
    # The licence asks for each dataset's link and access date in the citation
    accessed = accessed or date.today().isoformat()
    manifest = {code: {"url": DATASET_PAGE.format(code=code), "accessed": accessed} for code in codes}
    (raw_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def parse_cell(text):
    """Split a Eurostat cell into (value, flag). Either can be None."""
    parts = text.strip().split()
    if not parts:
        return None, None
    number, flag = parts[0], (parts[1] if len(parts) > 1 else None)
    value = None if number == ":" else float(number)
    return value, flag


def read_wide_tsv(path):
    """Yield one dict per cell: every dimension, plus geo, year, value and flag."""
    with open(path) as f:
        header = f.readline().rstrip("\n").split("\t")
        # The first header cell looks like "freq,size_emp,...,geo\TIME_PERIOD"
        dims = header[0].split("\\")[0].split(",")
        years = [int(h.strip()) for h in header[1:]]
        for line in f:
            cells = line.rstrip("\n").split("\t")
            key = dict(zip(dims, cells[0].split(",")))
            for year, cell in zip(years, cells[1:]):
                value, flag = parse_cell(cell)
                yield {**key, "year": year, "value": value, "flag": flag}


def read_codelist(path):
    """Return {code: English label} from a Eurostat codelist TSV."""
    labels = {}
    with open(path) as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2:
                labels[parts[0].strip()] = parts[1].strip()
    return labels
