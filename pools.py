# CAKE / BUNNY optimiser
#%%
cake_staked = 200000 # in GBP
cake_price = 28
bunny_price = 236
bnb_price = 456
fees_to_compound = 4
cake_pool_apr = 90

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


#%%

compound_interest(cake_staked, cake_pool_apr, 174, fees_to_compound)
# %%

a = optimal_interval(cake_staked, cake_pool_apr, fees_to_compound)

f"Compound when you have {a[0] / cake_price:.1f} cake, which is every {a[1]:.2f} days, leading to {a[2] / cake_price:.1f} in cake (worth £{a[2]:,.0f}) over one year with a APY of {a[3]:.2f}%"
# %%
