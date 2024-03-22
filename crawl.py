import requests
from bs4 import BeautifulSoup

def product_crawl(serial_number):
    product_base = 'https://www.uniqlo.com/jp/ja/products/'
    product_url = product_base + serial_number
    # first check if product exist in UniqloJP
    product_page = requests.get(product_url)
    if product_page.status_code == 404:
        return -1
    else:
        # search product in google
        search_base = "https://www.google.com/search?q=uniqlo+jp+"
        search_url = search_base + serial_number
        search_page = requests.get(search_url)
        soup = BeautifulSoup(search_page.text, "lxml")
        span_set = soup.find_all('span')[15:25]
        price_text = ""
        jp_price_in_twd = 0
        for span in span_set:
            span = span.get_text()
            if "¥" in span:
                price_text = span
                break
        # trim
        if "," in price_text:
            price_text = price_text.replace(',', '')
        if "¥" in price_text:
            price_text = price_text.replace('¥', '')
        if "JPY" in price_text:
            price_text = price_text.replace('JPY', '')
        price_jp = int(price_text)

        # currency exchange
        currency_url = "https://www.google.com/finance/quote/JPY-TWD"
        currency_page = requests.get(currency_url)
        soup = BeautifulSoup(currency_page.text, "lxml")
        exchange_rate = float(soup.find('div', class_='YMlKec fxKbKc').get_text())
        jp_price_in_twd = round(price_jp * exchange_rate)

        # find price in UQ 搜尋
        product_url_tw = "https://www.google.com/search?q=uniqlo+%E6%90%9C%E5%B0%8B+"
        product_url_tw += serial_number
        product_page_tw = requests.get(product_url_tw)
        soup_tw = BeautifulSoup(product_page_tw.text, "lxml")
        span_set_tw = soup_tw.find_all('span')[10:]
        price_text_tw = ""
        for span in span_set_tw:
            text = span.get_text()
            text_length = len(text)
            # if ".00" and "$" in text and text_length < 13:
            if ".00" and "$" in text:
                if "HK" not in text:
                    price_text_tw = text
                    break
                continue
        # trim
        if ".00" in price_text_tw:
            price_text_tw = price_text_tw.replace('.00', '')
        if "," in price_text_tw:
            price_text_tw = price_text_tw.replace(',', '')
        if "NT" in price_text_tw:
            price_text_tw = price_text_tw.replace('NT', '')
        if "$" in price_text_tw:
            price_text_tw = price_text_tw.replace('$', '')
        
        result = [serial_number, product_url, price_jp, jp_price_in_twd, price_text_tw]

        return result

            
# test, product list = [464787, 467536, 467543, 459591, 460926, 463503]
if __name__ == '__main__':
    pass
    
