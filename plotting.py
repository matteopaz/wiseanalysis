import plotly.graph_objects as go
import pandas as pd
import numpy as np

load = input("csv: ") + ".csv"

phase = 5.877

df = pd.read_csv("./saved/"+load)
df = df[["mjd", "w1mpro", "w1sigmpro", "qual_frame"]]
df.dropna(how="any", inplace=True)
df = df[df["qual_frame"] == 10]

df.sort_values(by="mjd", inplace=True)

w1 = df["w1mpro"].values
w1s = df["w1sigmpro"].values
# w2 = df["w2mpro"].values
# w2s = df["w2sigmpro"].values
mjd = df["mjd"].values


if phase != 0:
    mjd = (mjd % phase) / phase
    mjd = np.concatenate((mjd, mjd + 1))
    w1 = np.concatenate((w1, w1))
    w1s = np.concatenate((w1s, w1s))
    # w2 = np.concatenate((w2, w2))
    # w2s = np.concatenate((w2s, w2s))

    

w1_tr = go.Scatter(x=mjd, y=w1, name="W1",
                   error_y=dict(type="data", array=w1s, visible=True, color="rgba(0,0,0,0.55)", thickness=1.25), 
                   mode="markers", marker_symbol="square", marker=dict(size=5, color="rgba(0,0,0,0.55)"))
# w2_tr = go.Scatter(x=mjd, y=w2, name="W2",
#                   error_y=dict(type="data", array=w2s, visible=True, color="rgba(255,165,0,0.55)", thickness=1.25), 
#                   mode="markers", marker_symbol="square", marker=dict(size=5, color="rgba(255,165,0,0.55)"))

fig = go.Figure(data=[w1_tr])
fig.update_layout(
    font=dict(
        family="monospace",
        size=14,
        color="Black"
    ),
    xaxis_title="mjdate",
    yaxis_title="magnitude",
    width=800,
    height=600,
    plot_bgcolor='white',
    showlegend=True
)
fig.update_xaxes(
    mirror=True,
    ticks='outside',
    showline=True,
    linecolor='black',
    gridcolor='lightgrey'
)
fig.update_yaxes(
    mirror=True,
    ticks='outside',
    showline=True,
    linecolor='black',
    gridcolor='lightgrey',
    autorange="reversed"
)

fig.update_legends(
    orientation="v",
    x=0.985,
    y=0.985,
    xanchor="right",
    yanchor="top",
    bgcolor="white",
    bordercolor="black",
    borderwidth=1)

if phase != 0:
    fig.update_xaxes(title="phase")
    fig.update_layout(title="period="+str(phase)+"d", title_x=0.5)

name = "./saved/"+load[:-4]
if phase != 0:
    name += "_folded"
fig.write_image(name+".png")