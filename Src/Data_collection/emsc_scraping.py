from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException , StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.firefox.options import Options
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
from configs import JAPAN_EMSC_CSV

# run it from project root with: python -m Src.Data_collection.emsc_scraping 


#filling filters textboxes
def fill_filters(wait, css_selector, value, clamp_to_max=False):
    element = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
    )
    if clamp_to_max:
        max_allowed_str = element.get_attribute("max")
        if max_allowed_str:
            max_allowed_date = datetime.strptime(max_allowed_str, "%Y-%m-%d").date()
            if value > max_allowed_date:
                value = max_allowed_date
    element.clear()
    element.send_keys(str(value))
    return element



def emsc_data_earthquake_scrape(date_start:date, date_end:date, latitude_min:int, latitude_max:int, longitude_min:int, longitude_max:int, magnitude_min:int = 1, magnitude_max:int = None):

    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Firefox(options=options)
    wait = WebDriverWait(driver, 20)
    url = "https://www.emsc.eu/Earthquake_information/"
    all_data = []

    try:
        driver.get(url)

        fill_filters(wait, "input#datemin", date_start)
        fill_filters(wait, "input#datemax", date_end, clamp_to_max=True)

        fill_filters(wait, "input#magmin", magnitude_min)
        if magnitude_max is not None:
            fill_filters(wait, "input#magmax", magnitude_max)

        fill_filters(wait, "input#latmin", latitude_min)
        fill_filters(wait, "input#latmax", latitude_max)

        fill_filters(wait, "input#lonmin", longitude_min)
        fill_filters(wait, "input#lonmax", longitude_max)

        
        search_btn = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR,"input[value='Search']"))
        )
        search_btn.click()

        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, "div#nbres"),"Result"))

        while True:

            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr.lilist")))
            soup = BeautifulSoup(driver.page_source, "html.parser")

            rows = soup.find_all("tr", class_="lilist")
            for row in rows:

                date = row.find("td", class_="tbdat").get_text(strip=True)
                lat = row.find("td", class_="tblat").get_text(strip=True)
                lon = row.find("td", class_="tblon").get_text(strip=True)
                dep = row.find("td", class_="tbdep").get_text(strip=True)
                mag = row.find("td", class_="tbmag").get_text(strip=True)
                magtyp = row.find("td", class_="tbmagtyp").get_text(strip=True)
                reg = row.find("td", class_="tbreg").get_text(strip=True)
                
                all_data.append({
                    "date": date,
                    "latitude": lat,
                    "longitude": lon,
                    "depth": dep,
                    "magnitude": mag,
                    "magtype": magtyp,
                    "region": reg
                })

            try:
                #finding current page
                current_page = driver.find_element(By.CSS_SELECTOR, "div.pag.selview").text
                #finding next page button
                next_btn = driver.find_element(By.CSS_SELECTOR, "div.pag.spes.spes1")
            except NoSuchElementException:
                break  

            #checking if the page is the last page breaks loop
            if "oldpag" in next_btn.get_attribute("class"):
                break

            next_btn.click()

            #waiting until new page data laoded
            wait.until(
                lambda d: d.find_element(By.CSS_SELECTOR, "div.pag.selview").text != current_page
            )
            

        df = pd.DataFrame(all_data)
        df.to_csv(JAPAN_EMSC_CSV, index=False, encoding="utf-8-sig")

        return True
    
    except StaleElementReferenceException as e:
        print("stale", e)
        return False

    except TimeoutException as e:
        print("timeout")
        return False

    except:
        print("an error ocurred, Try again...")
        return False

    finally:
        driver.quit()



def emsc_japan_lastmonth():
    end_date = datetime.today().date() 
    start_date = end_date - timedelta(days=30)

    return emsc_data_earthquake_scrape(start_date, end_date, 24, 46, 123, 146, 1)


if __name__ == '__main__':

    if emsc_japan_lastmonth():
        
        print("DONE!")
