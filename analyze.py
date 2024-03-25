import astropy
import plotly.graph_objects as go
from astropy.coordinates import SkyCoord
from astroquery.simbad import Simbad
import numpy as np
import pandas as pd
import time
from math import trunc
import pyvo
import names


filename = "var"
service = pyvo.dal.TAPService("https://irsa.ipac.caltech.edu/TAP")

def querywise(ra, dec):
    rad = 3 / 3600
    rad = trunc(rad * 10**6) / 10**6
    qstr = """
    SELECT ra,dec,w1mpro,w1sigmpro,w1mpro,w2sigmpro,mjd,qual_frame
    FROM neowiser_p1bs_psd
    WHERE CONTAINS(POINT('ICRS',ra, dec),CIRCLE('ICRS',{},{},{}))=1
    """.format(ra,dec, rad)
    job = service.submit_job(qstr)
    return job.run()

def isinsimbad(ra, dec):
    c = SkyCoord(ra=ra, dec=dec, unit=(astropy.units.deg, astropy.units.deg), frame='icrs')
    rad = 4.5 * astropy.units.arcsec
    r= Simbad.query_region(c, radius=rad)
    if r:
        return True
    return False

def process(res):
    res = res.wait()
    res = res.fetch_result()
    tbl = res.to_table().to_pandas()
    tbl = tbl[tbl.qual_frame >= 9]
    return tbl

def plot(name, tbl):
    tbl = tbl.sort_values(by="mjd")
    tbl["mjd"] = tbl["mjd"] - tbl["mjd"].min()
    y = tbl["w1mpro"].values
    x = tbl["mjd"].values
    fig = go.Figure()
    tr = go.Scatter(x=x, y=y, mode="markers", marker=dict(size=6, opacity=.65, color="black"))
    fig.add_trace(tr)
    fig.update_layout(
        font=dict(
            family="monospace",
            size=14,
            color="Black"
        ),
        title=name,
    )
    fig.update_yaxes(autorange="reversed")
    fig.show()
    

df = pd.read_csv(filename + ".csv")
df["simbad_match"] = [False for _ in range(len(df))]
df["score"] = [0 for _ in range(len(df))]

queries = []
bufferspacing = 25

for i in range(bufferspacing): # Initial buffer
    ra = df.iloc[i]["ra"]
    dec = df.iloc[i]["dec"]
    q = querywise(ra, dec)
    queries.append(q)
    simbad_match = isinsimbad(ra, dec)
    df.at[i, "simbad_match"] = simbad_match

for i, row in df.iterrows():
    print("Processing", i, "of", len(df))   
    q = queries[i]

    if i < len(df) - bufferspacing:
        rabuff = df.iloc[i + bufferspacing - 1]["ra"]
        decbuff = df.iloc[i + bufferspacing - 1]["dec"]
        qbuff = querywise(rabuff, decbuff)
        queries.append(qbuff)

        try:
            simbad_match = isinsimbad(rabuff, decbuff)
        except:
            simbad_match = False
        df.at[i, "simbad_match"] = simbad_match

    q = process(q)

    plot("Row {} @ {} {}".format(str(i), ra, dec), q)

    inp = input("Flag? (y/n): ")

    if inp == "y": # ALRIGHT
        df.at[i, "flagged"] = 1
        print("Flagged:", df.at[i, "flagged"])
    if inp == "yy": # VERY GOOD
        df.at[i, "flagged"] = 2
        print("Flagged:", df.at[i, "flagged"])
    if inp == "yyy": # OUTSTANDING
        df.at[i, "flagged"] = 3
        print("Flagged:", df.at[i, "flagged"])
    if inp == "v": # Likely Misclassified but anomalous
        df.at[i, "flagged"] = -1
        print("Flagged:", df.at[i, "flagged"])

    if inp == "s": # Save
        df.at[i, "flagged"] = 3
        print("Flagged:", df.at[i, "flagged"])
        with open("./saved/"+names.get_first_name()+".csv", "w") as f:
            q.to_csv(f)
        

    df.to_csv(filename+"_scored.csv", index=True)
    if inp == "stop":
        raise SystemExit("Stopped and saved")

df.to_csv(filename+"_scored.csv", index=True)


    
