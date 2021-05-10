import streamlit as st
import altair as alt
import pandas as pd
import requests



def get_prices():
    price_url ='https://api.coingecko.com/api/v3/simple/price?ids=pancakeswap-token%2Cbinancecoin%2Cpancake-bunny&vs_currencies=gbp'

    response = requests.get(url = price_url)
    price_data = response.json()
    
    global cake_price
    global bunny_price
    global bnb_price
    global fees_to_compound
    global cake_pool_apr

    cake_price = price_data['pancakeswap-token']['gbp']
    bunny_price = price_data['pancake-bunny']['gbp']
    bnb_price = price_data['binancecoin']['gbp']

    fees_in_bnb = 0.00600979
    fees_to_compound = fees_in_bnb * bnb_price
    cake_pool_apr = 104.05  # %

    return None

get_prices()




def simple_interest(amount, interest):
    """Calculates interest for fixed period

    Args:
        amount ([float]): The starting amount
        interest ([float]): Interest rate in %, e.g. 90% would be 90

    Returns:
        [float]: The total amount including interest
    """
    return amount * (1 + interest / 100)


def compound_interest(amount, annual_interest, periods, fees, days = 365):
    """Calculate total returns based upon periodic compounding

    Args:
        amount ([float]): The starting amount
        annual_interest ([float]): Interest rate annually in %, e.g. 90% would be 90
        periods ([int]): Number of times to compound
        fees ([float]): Fees to compound, e.g. claiming and staking
        days ([int]): Number of days over which periods are defined

    Returns:
        [float]: The total amount including interest and fees
    """    
    days_per_period = days / periods
    period_interest = annual_interest / 365 * days_per_period

    for _ in range(periods):
        amount = simple_interest(amount, period_interest) - fees


    return amount

def compound_interest_bunny(amount, annual_interest, periods, fees, days = 365):
    """Calculate total returns based upon periodic compounding

    Args:
        amount ([float]): The starting amount
        annual_interest ([float]): Interest rate annually in %, e.g. 90% would be 90
        periods ([int]): Number of times to compound
        fees ([float]): Fees to compound, e.g. claiming and staking
        days ([int]): Number of days over which periods are defined

    Returns:
        [float]: The total amount including interest and fees
    """    
    days_per_period = days / periods
    period_interest = annual_interest / 365 * days_per_period

    for _ in range(periods):
        amount = amount + amount * period_interest / 100 * 0.7 + amount * period_interest / 100 * 0.3 * 3 * bunny_price / bnb_price - fees


    return amount


def optimal_interval(amount, annual_interest, fees):
    final_amount = compound_interest(amount, annual_interest, periods=1, fees=fees)
    optimum_periods = 1
    while True:
        next_result = compound_interest(amount, annual_interest, periods=optimum_periods + 1, fees=fees)
        if next_result <= final_amount:
            break
        optimum_periods += 1
        final_amount = next_result
    
    first_compound_amount = simple_interest(amount, annual_interest / optimum_periods) - amount
    compound_frequency = 365 / optimum_periods
    real_apy = 100 * (final_amount - amount) / amount

    return first_compound_amount, compound_frequency, final_amount, real_apy


# Cake Staking on bunny


def optimal_interval_bunny(amount, annual_interest, fees):
    final_amount = compound_interest_bunny(amount, annual_interest, periods=1, fees=fees)
    optimum_periods = 1
    while True:
        next_result = compound_interest_bunny(amount, annual_interest, periods=optimum_periods + 1, fees=fees)
        if next_result <= final_amount:
            break
        optimum_periods += 1
        final_amount = next_result
    
    first_compound_amount = simple_interest(amount, annual_interest / optimum_periods) - amount
    compound_frequency = 365 / optimum_periods
    real_apy = 100 * (final_amount - amount) / amount

    return first_compound_amount, compound_frequency, final_amount, real_apy


def print_results(results):
    lines = (
        f"Compound when you have {results[0] / cake_price:.1f} cake, which is every {results[1]:.2f} days. ",
        f"Leading to {results[2] / cake_price:.1f} in cake (worth £{results[2]:,.0f}) over one year with a APY of {results[3]:.2f}%"
    )
    # return f"Compound when you have {results[0] / cake_price:.1f} cake, which is every {results[1]:.2f} days. Leading to {results[2] / cake_price:.1f} in cake (worth £{results[2]:,.0f}) over one year with a APY of {results[3]:.2f}%"
    return lines

def print_results_bunny(results):
    lines = (
        f"Compound when you have {results[0] * 0.7 / cake_price:.1f} cake, which is every {results[1]:.2f} days. ",
        f"Leading to {results[2] / cake_price:.1f} in cake (worth £{results[2]:,.0f}) over one year with a APY of {results[3]:.2f}%"
    )
    # return f"Compound when you have {results[0] / cake_price:.1f} cake, which is every {results[1]:.2f} days. Leading to {results[2] / cake_price:.1f} in cake (worth £{results[2]:,.0f}) over one year with a APY of {results[3]:.2f}%"
    return lines


def winner(pancake, bunny):
    if pancake[2] > bunny[2]:
        winner = "Pancake"
        amount = pancake[2] - bunny[2]
    else:
        winner = "Bunny"
        amount = bunny[2] - pancake[2]
    
    return winner, amount


st.title('🐰Pancakebunny CAKE🍰 Compounder')
st.write("Working out how often you should compound your CAKE. \
Assumes you swap BUNNY back to CAKE to stake.")
st.write("Should you stake on [pancakeswap](https://pancakeswap.finance/pools) or [bunnyswap](https://pancakebunny.finance/pool/CAKE)?")
cake_staked = st.number_input(label='Enter CAKE staked in £:', value=1000)
st.write("")

pancakeswap = optimal_interval(cake_staked, cake_pool_apr, fees_to_compound)
bunnyswap = optimal_interval_bunny(cake_staked, cake_pool_apr, fees_to_compound)

st.write(f"🍰 £{cake_price:,.2f}, 🐰 £{bunny_price:,.2f}, 💰BNB £{bnb_price:,.2f}")

st.write("## On Pancakeswap:")
st.write(print_results(pancakeswap)[0])
st.write(print_results(pancakeswap)[1])
st.write("## On Pancakebunny:")
st.write(print_results_bunny(bunnyswap)[0])
st.write(print_results_bunny(bunnyswap)[1])

df = pd.DataFrame({'Days': range(1, 366)})
df['Pancakeswap'] = df['Days'] / 365 * pancakeswap[3] / 100 * cake_staked + cake_staked
df['Bunnyswap'] = df['Days'] / 365 * bunnyswap[3] / 100 * cake_staked + cake_staked

# st.dataframe(df.style.format({'Pancakeswap': '£{:,.0f}', 'Bunnyswap': '£{:,.0f}'}))

st.subheader("Compare performance over time")

chart_data = df.melt('Days')
chart_data.columns = ['Days', 'Platform', 'Amount']

c = alt.Chart(chart_data).mark_line().encode(
    x=alt.X('Days'),
    y=alt.Y('Amount', axis=alt.Axis(format=',.0f'), title="Amount (£)"),
    color='Platform'
).interactive()

st.altair_chart(c, use_container_width=True)

st.header("The winner?")

winner, amount = winner(pancakeswap, bunnyswap)

st.write(f"Is... {winner}! Earning you £{amount:,.0f} more.")


