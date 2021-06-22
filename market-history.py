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
all_data['gotchi.stakedAmount'] = all_data['gotchi.stakedAmount'].astype(float)
all_data['gotchi.stakedAmount'] = all_data['gotchi.stakedAmount'] / 1e18
all_data = all_data.drop(columns=['priceInWei'], axis=1)

# remove non-numeric columns
cols = all_data.columns.drop(['buyer', 'seller',
       'gotchi.equippedWearables', 'gotchi.name', 'gotchi.collateral',
       'gotchi.numericTraits'])

all_data[cols] = all_data[cols].apply(pd.to_numeric, errors='coerce')
all_data = all_data[all_data['gotchi.baseRarityScore'] != 0]

#%%

# replace collateral with tokens

replace_values = {
'0x9719d867a500ef117cc201206b8ab51e794d3f82': 'maUSDC',
'0xe0b22e0037b130a9f56bbb537684e6fa18192341': 'maDAI',
'0xdae5f1590db13e3b40423b5b5c5fbf175515910b': 'maUSDT',
'0xf4b8888427b00d7caf21654408b7cba2ecf4ebd9': 'maTUSD',
'0x20d3922b4a1a8560e1ac99fba4fade0c849e2142': 'maWETH',
'0x823cd4264c1b951c9209ad0deaea9988fe8429bf': 'maAAVE',
'0x8c8bdbe9cee455732525086264a4bf9cf821c498': 'maUNI',
'0xe20f7d1f0ec39c4d5db01f53554f2ef54c71f613': 'maYFI',
'0x98ea609569bd25119707451ef982b90e3eb719cd': 'maLINK'
}

all_data['gotchi.collateral'] = all_data['gotchi.collateral'].replace(replace_values, regex=True)

#%%
# rename all columns

all_data = all_data.rename(columns={"id": "Listing", "buyer": "Buyer", "seller": "Seller",
"timePurchased": "Block Sold", "gotchi.baseRarityScore": "BRS", "gotchi.collateral": "Collateral",
'gotchi.equippedWearables':'Wearables List', 'gotchi.experience': 'XP', 'gotchi.id': 'Aavegotchi ID',
       'gotchi.kinship': 'Kinship', 'gotchi.modifiedRarityScore': 'MRS', 'gotchi.name': 'Name',
       'gotchi.numericTraits': 'Traits List', 'gotchi.stakedAmount': 'Staked Amount', })

# %%
# traits

all_data[['NRG', 'AGG', 'SPK', 'BRN', 'EYS', 'EYC']] = pd.DataFrame(all_data['Traits List'].tolist(), index = all_data.index)
all_data = all_data.drop(columns=['Traits List'], axis=1)
#%%
all_data.to_excel('gotchi.xlsx')
# %%
