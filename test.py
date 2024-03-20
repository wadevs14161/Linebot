if __name__ == "__main__":
    price_text_tw = "$HK199.00"
    if "HK" not in price_text_tw:
        print("NO HK")




    price_text_tw = "$390.00 至 $990.00"
    if ".00" in price_text_tw:
        # price_text_tw = price_text_tw[:-3]
        price_text_tw = price_text_tw.replace('.00', '')
    if "," in price_text_tw:
        price_text_tw = price_text_tw.replace(',', '')
    if "NT" in price_text_tw:
        price_text_tw = price_text_tw.replace('NT', '')
    if "$" in price_text_tw:
        price_text_tw = price_text_tw.replace('$', '')
    print(price_text_tw)