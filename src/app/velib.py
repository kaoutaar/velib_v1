import streamlit as st
import pandas as pd
import json
import numpy as np
import matplotlib.image as mpimg
from PIL import Image
import os
import glob

dir = './streampool/data'
with open("./data/locations") as f:
    locations = ["Search 🔍"] + json.load(f)

st.set_page_config(layout="wide")
bike_img = mpimg.imread("./images/istockphoto-1333015759-612x612(1).jpg")
stand_img = mpimg.imread("./images/istockphoto-1333015759-612x612.jpg")
image = Image.open('./images/original-ab909353e08d02cf7c952047ab00a039.jpg')

def read_data(dir):
    files = glob.glob(dir+'/*.parquet')
    while len(files) == 0:
        files = glob.glob(dir+'/*.parquet')
    file=files[0]
    data= pd.read_parquet(file)
    return data

data = read_data(dir).sort_values(["name", "last_update"], ascending=[True, False]).groupby("name").first()
last_update = os.path.getmtime(dir)

def show_metrics():
    global last_update
    global data

    #refresh if new data is in
    cur_update = os.path.getmtime(dir)
    if cur_update>last_update:
        data = read_data(dir).sort_values(["name", "last_update"], ascending=[True, False]).groupby("name").first()
        last_update = cur_update


    cont1 = c.container()
    col00, col0, col1, col2, col3 = cont1.columns([5,2,10, 2,8])

    location = st.session_state["station"]
    if "Search" in location:
        pass

    else:
        av_bikes = data.loc[location, "available_bikes"]
        av_stands = data.loc[location, "available_bike_stands"]
        isopen = "✅" if data.loc[location, "status"]=="OPEN" else "❌"
        isbank = "✅" if data.loc[location, "banking"]==True else "❌"
        isbonus = "✅" if data.loc[location, "bonus"]==True else "❌"

        col00.write('')
        col0.metric("space", value="", label_visibility="hidden")
        col0.markdown(f"<h1 style='text-align: left; color: clack;'>{av_bikes}</h1>", unsafe_allow_html=True)
        col1.image(bike_img, width=150)
        col2.metric("space", value="", label_visibility="hidden")
        col2.markdown(f"<h1 style='text-align: left; color: clack;'>{av_stands}</h1>", unsafe_allow_html=True)
        col3.image(stand_img, width=150)

        cont2 = c.container()
        col0, col1, col2, col3 = cont2.columns([1,1.5,1.5, 1.5])

        col0.write('')
        col1.title("")
        col1.metric("Open", value=isopen)
        col2.title("")
        col2.metric("Banking", value=isbank)
        col3.title("")
        col3.metric("Bonus", value=isbonus)

c = st.container()
c.image(image)
c.selectbox("stations",options=locations, key="station", on_change=show_metrics, label_visibility="hidden")

