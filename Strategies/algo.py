def sort_func(rsi_obj):
    return rsi_obj.RSI[-1]
def rank(RSIs):
    return sorted(RSIs, key=sort_func)
def checkToSell(RSI):
    if RSI < 70:
        return True
    return False
