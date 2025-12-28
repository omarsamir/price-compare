import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_jumia_price():
    url = "https://www.jumia.com.eg/en/catalog/?q=samsung+galaxy+a56"
    response = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(response.text, "lxml")

    product = soup.select_one("article.prd")
    if not product:
        return None

    name = product.select_one("h3.name").text.strip()
    price = product.select_one("div.prc").text.strip().replace("EGP", "").strip()

    print("JUM prod name: ",name)
    print("JUM prod Price: ",price)
    
    return {
        "site": "Jumia",
        "product": name,
        "price": price,
        "currency": "EGP"
    }


def get_amazon_price(url, timeout=15):
    options = Options()
    # Use visible browser to avoid bot detection
    options.add_argument("--window-size=1920,1080")
    # Set a realistic User-Agent
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        wait = WebDriverWait(driver, timeout)

        with open("amzn.html", "w", encoding="utf-8") as file:
            file.write(str(driver.page_source))

        title_elem = wait.until(
            EC.presence_of_element_located((By.ID, "productTitle"))
        )

        price_elem =  wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.a-price-whole"))
        )
    
        return {
        "site": "Amazon",
        "product": title_elem.text.strip(),
        "price": price_elem.text.strip(),
        "currency": "EGP"
    }
    except Exception as e:
        print("Error:", e)
        return None
    finally:
        driver.quit()



def main():
    data = []

    jumia = get_jumia_price()
    if jumia:
        data.append(jumia)

    amazon = get_amazon_price(url= "https://www.amazon.eg/-/en/Samsung-Smartphone-Lightgray-Upgrades-Warranty/dp/B0DZHNZ1L2/")
    if amazon:
        data.append(amazon)

    if not data:
        print("No data collected")
        return

    df = pd.DataFrame(data)
    df["date"] = datetime.now().strftime("%Y-%m-%d")

    df.to_csv("output/price_report.csv", index=False)
    print("✅ Price report generated successfully")


if __name__ == "__main__":
    main()
