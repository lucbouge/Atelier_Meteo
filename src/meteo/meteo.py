import pandas as pd
import requests
import matplotlib.pyplot as plt
import re
from datetime import datetime

METEO_URL = (
    "https://www.data.gouv.fr/fr/datasets/r/45ffe00f-6b32-4093-93b3-66c0eef3704e"
)
CSV_GZ_FILENAME = "meteo.csv.gz"
RENNES_SAINT_JACQUES = "RENNES-ST JACQUES"

# Description des champs:
# https://www.data.gouv.fr/fr/datasets/r/bbe124c5-58e5-4c51-ab0a-b6847bbef528
# INST        : durée d’insolation quotidienne (en mn)

FIELD1 = "INST"
FIELD2 = "PMERM"
ROLLING_SCOPE = 30

################################################################################


def main():
    filename = get_csv_gz_file(url=METEO_URL, filename=CSV_GZ_FILENAME)
    df = make_meteo_df(filename=filename, station=RENNES_SAINT_JACQUES)
    data1 = make_data(df=df, field=FIELD1, rolling_scope=ROLLING_SCOPE)
    data2 = make_data(df=df, field=FIELD2, rolling_scope=ROLLING_SCOPE)
    title = f"Data: {FIELD1} + {FIELD2}, Rolling scope: {ROLLING_SCOPE}"
    show_data(data1=data1, field1=FIELD1, data2=data2, field2=FIELD2, title=title)


def make_data(*, df, field, rolling_scope):
    df = df[["AAAAMMJJ", field]]
    date = df["AAAAMMJJ"].apply(AAAAMMJJ_to_date)
    df = df.set_index(date)
    data = df[field]
    data = data.rolling(rolling_scope).mean()
    max = data.max()
    min = data.min()
    data = ((data - min) / (max - min)) * 100
    return data


def show_data(*, data1, field1, data2, field2, title):
    fig, ax = plt.subplots()
    fig.autofmt_xdate()
    ax.grid(True)
    ax.set_title(title)
    ax.plot(data1, label=field1)
    ax.plot(data2, label=field2)
    ax.legend()
    plt.show()


################################################################################


def AAAAMMJJ_to_date(s: int) -> datetime:
    m = re.fullmatch(r"(\d{4})(\d{2})(\d{2})", str(s))
    assert m is not None, s
    (year, month, day) = m.groups()
    date = datetime(year=int(year), month=int(month), day=int(day))
    return date


def make_meteo_df(*, filename, station):
    df = pd.read_csv(filename, compression="gzip", sep=";", dtype="string")
    df = df[df["NOM_USUEL"] == station]
    return df


def get_csv_gz_file(*, url, filename):
    r = requests.get(url)
    assert r.ok, url
    with open(filename, "wb") as fd:
        fd.write(r.content)
    return filename


################################################################################

main()
