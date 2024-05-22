from helper import *


def main():
    # Example usage

    wallet_address = "2RcEamY9tuMLbQep28BqTK2kpByy95iT6bdXqgNHUADC"
    mint_address = "5NejGhNyARVgGSZ8jiqiBdqkiZbYHxTjMN9sMqLmuBKS"
    

    ###### GET Balance Token ####################################
    # Example usage
    #
    # balance_info = get_balance(wallet_address, mint_address)
    # print(f"Balance info: {balance_info}")
    ##############################################################


    #### GET QUOTE FUNCTION ####################################
    # quote_type = "sell"  # "buy" or "sell"
    # mint = "5NejGhNyARVgGSZ8jiqiBdqkiZbYHxTjMN9sMqLmuBKS"  # Token mint address
    # amount = 33067  # Amount in lamports (0.0001 SOL)
    # slippage = 5  # Desired slippage
    # quote = get_quote(quote_type, mint, amount, slippage)




    ##### PERFORM BUY TRADE #######################################3
    # Parameters
    wallet_address = "2RcEamY9tuMLbQep28BqTK2kpByy95iT6bdXqgNHUADC"
    mint_address = "5NejGhNyARVgGSZ8jiqiBdqkiZbYHxTjMN9sMqLmuBKS"
    slippage = 5
    private_key = "446q9tCCkzdrHxsfSiTQMzK2DWBVjJqH13Y2DaN5nHbrahsyuVmhnqJvMrE24b7BMjEAN72MXwnvnyrzKpAa19t2"

    # Perform a sell trade for 50% of the token balance
    perform_sell_trade(wallet_address, mint_address, 100, slippage, private_key)

    #############################################################


   
main()
