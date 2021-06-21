#%%
import requests
import pandas as pd
from string import Template

# todo
# remove zeros from results
# expand traits
# clean up columns
# lookup wearables list
# download all gotchi, and estimate price


#%%
queryTemplate = Template("""
{
    erc721Listings(
      first: 1000,
      skip: $skip,
      where: {
        category:3,
        buyer_not: null
      },
      orderBy: timePurchased,
      orderDirection: desc
    ) {
      id
      priceInWei
      timePurchased
      seller
      buyer
      gotchi {
        id
        name
        baseRarityScore
        modifiedRarityScore
        kinship
        experience
        collateral
        stakedAmount
        equippedWearables
        numericTraits
      }
    }
  }
"""
)
#%%
def run_query(query):
    request = requests.post('https://api.thegraph.com/subgraphs/name/aavegotchi/aavegotchi-core-matic', json={'query': query})
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

def json_to_df(json):
    return pd.json_normalize(json['data']['erc721Listings'])

#%%
# async this 

all_data = pd.DataFrame()
for i in range(10):
    skip = i * 1000
    data = json_to_df(run_query(queryTemplate.substitute(skip=skip)))
    if len(data) > 0:
        all_data = all_data.append(data)
    else: break


# %%
all_data['priceInWei'] = all_data['priceInWei'].astype(float)
all_data['GHST'] = all_data['priceInWei'] / 1e18
# %%

all_data.to_excel('gotchi.xlsx')
# %%

# %%
