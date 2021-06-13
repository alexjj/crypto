import streamlit as st
import altair as alt
import pandas as pd
import requests

portals_url ='https://api.aavegotchi.land/open_portal_listing?desired_traits=x,x,x,x,x,x&order_by=min_brs'
gotchi_url ='https://api.aavegotchi.land/gotchi_listing?desired_traits=x,x,x,x,x,x&brs_min=0&brs_max=1000&price_min=0&&price_max=1000000&order_by=brs'

def get_data(url):
    response = requests.get(url=url)
    return response.json()

portals = pd.DataFrame(get_data(portals_url))
portals['brs/ghst'] = portals.max_brs / portals.price

portals_display = portals[['id','price','max_brs','listing_url', 'brs/ghst']]
portals_display.set_index('id', inplace=True)

gotchi = pd.DataFrame(get_data(gotchi_url))
gotchi['brs'] = pd.to_numeric(gotchi['brs'])
gotchi['mbrs'] = pd.to_numeric(gotchi['mbrs'])
gotchi['brs/ghst'] = gotchi.mbrs / gotchi.price
gotchi_display = gotchi[['name','price','mbrs','listing_url', 'brs/ghst']]
gotchi_display.set_index('name', inplace=True)

st.title('👻 Aavegotchi bargain hunter 💰')
st.write("Find the best value gotchi on the market. \
Aimed at new frens wanting to get into it without spending a fortune!")

st.image("meme.jpg", caption="So you missed Haunt 1")

st.write("## Gotchi for sale")
st.write("Top 20, sorted by rarity per GHST")
st.table(gotchi_display.sort_values(by=['brs/ghst'], ascending=False).head(20))

st.write("## Open portals for sale")
st.write("Top 20, sorted by rarity per GHST")
st.table(portals_display.sort_values(by=['brs/ghst'], ascending=False).head(20))


st.write("Thanks to aavegotchi.land for the API")