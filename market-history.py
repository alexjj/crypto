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
gotchi_sales_query = Template("""
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

wearable_sales_query = Template("""
{
    erc1155Purchases(
      first: 1000,
      skip: $skip,
      where: {
       category: 0,
       quantity_gt: 0
      },
      orderBy:timeLastPurchased,
      orderDirection:desc
    ) {
      id
      priceInWei
      erc1155TypeId
      timeLastPurchased
      quantity
      seller
      buyer
      listingID
    }
  }
""")


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

gotchi_sales = pd.DataFrame()
for i in range(10):
    skip = i * 1000
    data = json_to_df(run_query(gotchi_sales_query.substitute(skip=skip)))
    if len(data) > 0:
        gotchi_sales = gotchi_sales.append(data)
    else: break


# %%
gotchi_sales['priceInWei'] = gotchi_sales['priceInWei'].astype(float)
gotchi_sales['Price (GHST)'] = gotchi_sales['priceInWei'] / 1e18
gotchi_sales['gotchi.stakedAmount'] = gotchi_sales['gotchi.stakedAmount'].astype(float)
gotchi_sales['gotchi.stakedAmount'] = gotchi_sales['gotchi.stakedAmount'] / 1e18
gotchi_sales = gotchi_sales.drop(columns=['priceInWei'], axis=1)

# remove non-numeric columns
cols = gotchi_sales.columns.drop(['buyer', 'seller',
       'gotchi.equippedWearables', 'gotchi.name', 'gotchi.collateral',
       'gotchi.numericTraits'])

gotchi_sales[cols] = gotchi_sales[cols].apply(pd.to_numeric, errors='coerce')
gotchi_sales = gotchi_sales[gotchi_sales['gotchi.baseRarityScore'] != 0]

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

gotchi_sales['gotchi.collateral'] = gotchi_sales['gotchi.collateral'].replace(replace_values, regex=True)

#%%
# rename all columns

gotchi_sales = gotchi_sales.rename(columns={"id": "Listing", "buyer": "Buyer", "seller": "Seller",
"timePurchased": "Block Sold", "gotchi.baseRarityScore": "BRS", "gotchi.collateral": "Collateral",
'gotchi.equippedWearables':'Wearables List', 'gotchi.experience': 'XP', 'gotchi.id': 'Aavegotchi ID',
       'gotchi.kinship': 'Kinship', 'gotchi.modifiedRarityScore': 'MRS', 'gotchi.name': 'Name',
       'gotchi.numericTraits': 'Traits List', 'gotchi.stakedAmount': 'Staked Amount', })

# %%
# traits

gotchi_sales[['NRG', 'AGG', 'SPK', 'BRN', 'EYS', 'EYC']] = pd.DataFrame(gotchi_sales['Traits List'].tolist(), index = gotchi_sales.index)
gotchi_sales = gotchi_sales.drop(columns=['Traits List'], axis=1)

# wearables
gotchi_sales['Naked'] = gotchi_sales['Wearables List'] == "[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]"

gotchi_sales['Body'] = gotchi_sales['Wearables List'].str[0]
gotchi_sales['Face'] = gotchi_sales['Wearables List'].str[1]
gotchi_sales['Eyes'] = gotchi_sales['Wearables List'].str[2]
gotchi_sales['Head'] = gotchi_sales['Wearables List'].str[3]
gotchi_sales['Left Hand'] = gotchi_sales['Wearables List'].str[4]
gotchi_sales['Right Hand'] = gotchi_sales['Wearables List'].str[5]
gotchi_sales['Pet'] = gotchi_sales['Wearables List'].str[6]
gotchi_sales['Background'] = gotchi_sales['Wearables List'].str[7]

gotchi_sales = gotchi_sales.drop(columns=['Wearables List'], axis=1)

wearables_data_url = 'https://raw.githubusercontent.com/programmablewealth/aavegotchi-stats/master/src/data/wearables/wearables.json'
wearables_data = requests.get(wearables_data_url).json()
wearables_name = {i:wearables_data[str(i)]["0"] for i in wearables_data}

gotchi_sales['Body Item'] = gotchi_sales['Body'].apply(lambda x: 'NaN' if x == 0 else wearables_data[str(x)]["0"])

#%%


#%%
gotchi_sales.to_excel('gotchi.xlsx')
# %%
import dtale
d = dtale.show(gotchi_sales)
d
# %%
