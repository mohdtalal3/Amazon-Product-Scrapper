# Import Dependencies
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import subprocess
from dotenv import load_dotenv
import json
import re
import random
import time
load_dotenv()

def random_sleep(min_time, max_time):
    sleep_time = random.uniform(min_time, max_time)
    #print(f"Sleeping for {sleep_time:.2f} seconds..")
    sleep(sleep_time)

def extract_product_about_details(main_driver):
    text=""
    try:
        details=main_driver.find_elements(By.XPATH,'''//ul[contains(@class, 'a-unordered-list') and contains(@class, 'a-vertical') and contains(@class, 'a-spacing-small')]''')
 #       print(len(details))
        for detail in details:
            text=text+detail.text+'\n'
            
    except:
        try:
            details=main_driver.find_elements(By.XPATH,'''//ul[contains(@class, 'a-unordered-list') and contains(@class, 'a-vertical') and contains(@class, 'a-spacing-mini')]''')
            for detail in details:
                text=text+detail.text+'\n'   
        except:
            return None

    return text
    

def extract_product_code(url):
    pattern = r'/dp/([A-Z0-9]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        return None


def extract_price(main_driver):
    try:
        price=main_driver.find_element(By.XPATH,"//span[@class='a-price aok-align-center reinventPricePriceToPayMargin priceToPay']//span[@aria-hidden='true']")
        return price.text
    except:
        try:
            price=main_driver.find_elements(By.XPATH,"//span[@aria-hidden='true'][contains(text(),'$')]")
            if len(price) ==1:
                return price[0].text
            elif len(price)>=2:
                return price[0].text+'-'+price[1].text
        except:
            return None
        
def extract_image(main_driver):
    image_dict={}
    try:
        landing_image=main_driver.find_element(By.XPATH,"//li[contains(@class, 'image')]//img[contains(@class, 'a-dynamic-image')]")
        landing_image=landing_image.get_attribute('src')
        #print(landing_image)
        image_dict['Landing_Image']=landing_image
    except:
        image_dict['Landing_Image']=None
    try:
        images=main_driver.find_elements(By.XPATH,'//div[@id="altImages"]//li[contains(@class, "item")]//img')
        i_list=[]
        for image in images:
            # img=main_driver.find_element(By.TAG_NAME,"img")
            # print(img)
            image=image.get_attribute('src')
            i_list.append(image)
        image_dict['Other Images']=i_list
    except:
        image_dict['Other Images']=None
    return image_dict


def extract_colors(main_driver):
    try:
        color_list=[]
        print("Enter 2 image phase")
        options=main_driver.find_elements(By.XPATH,"//li[contains(@id, 'color_name_')]")
        if not options:  # Check if options list is empty
            print("No options found")
            raise Exception("No options found")  # Raise an exception to enter the except block
        for option in options:
            option.click()
            random_sleep(3, 5)  # Random sleep between 3 to 5 seconds
            color_dict={}
            images=extract_image(main_driver)
            try:
                color=option.find_element(By.XPATH,'//div[@class="a-row"]/span[@class="selection"]')
                color=color.text
                price=extract_price(main_driver)
                color_dict['Color']=color
                color_dict['Price']=price
                color_dict['Images']=images
                color_list.append(color_dict)
            except:
                print("Color name not found")
                raise Exception("Color name not found")  # Raise an exception to enter the except block
    except Exception as e:  # Catch the raised exceptions
        print("Exception occurred:", str(e))
        color_list1=[]
        color_dict1={}
        price=extract_price(main_driver)
        images=extract_image(main_driver)
        color_dict1['Color']=None
        color_dict1['Price']=price
        color_dict1['Images']=images
        color_list1.append(color_dict1)
        return color_list1
    return color_list


def fetch_star(text):
    import re
    pattern = r'a-star-(\d+)'
    match = re.search(pattern, text)
    if match:
        rating = match.group(1) 
        return rating
    else:
        print("No rating found in the statement.")
        return text

def extract_reviews(main_driver):
    reviews=[]
    try:
        #print("Fetching Reviews")
        review_path=main_driver.find_element(By.XPATH,"//a[normalize-space()='See more reviews']")
        review_link=review_path.get_attribute('href')
        main_driver.execute_script("window.open(arguments[0], '_blank');", review_link)
        main_driver.switch_to.window(main_driver.window_handles[-1])
        random_sleep(5, 8)  # Random sleep between 5 to 8 seconds
        for i in range(0,10):
            #extract_stars=main_driver.find_elements(By.XPATH,"//*[contains(@id, 'customer_review')]/div[2]/a/i")
            extract_stars=main_driver.find_elements(By.XPATH,"//i[@data-hook='review-star-rating']")
            extract_content=main_driver.find_elements(By.XPATH,"//span[@data-hook='review-body']")
            for star_element, content_element in zip(extract_stars, extract_content):
                if star_element and content_element is not None:
                    star_rating = star_element.get_attribute("class")
                    star_rating=fetch_star(star_rating)
                    review_content = content_element.text
                    review={}
                    review['stars']=star_rating
                    review['content']=review_content
                    reviews.append(review)
            try:
                next_page=main_driver.find_element(By.XPATH,"//a[contains(text(),'Next page')]")
                next_page.click()
                random_sleep(3, 5)  # Random sleep between 3 to 5 seconds
            except:
                main_driver.close()
                main_driver.switch_to.window(main_driver.window_handles[-1])
                random_sleep(3, 5)  # Random sleep between 3 to 5 seconds
                return reviews
    except:
        #main_driver.close()
        #main_driver.switch_to.window(main_driver.window_handles[-1])
        random_sleep(3, 5)  # Random sleep between 3 to 5 seconds
        return None
    time.sleep(2)
    main_driver.close()
    main_driver.switch_to.window(main_driver.window_handles[-1])
    random_sleep(3, 5)  # Random sleep between 3 to 5 seconds
    return reviews


def extract_product_details(main_driver,product_dict):
    try:
        brand_name=main_driver.find_element(By.XPATH,'//div[@id="bylineInfo_feature_div"]')
        brand_name=brand_name.text.lower()
        brand_name = brand_name.replace("visit the", "").strip()
        product_dict['Brand_Name']=brand_name
    except:
        product_dict['Brand_Name']=None

    url = main_driver.current_url
    asin=extract_product_code(url)
    product_dict['Asin']=asin
    try:
        product_title=main_driver.find_element(By.XPATH,'//span[@id="productTitle"]')
        product_title=product_title.text
        #print(product_title)
        product_dict['Product_Title']=product_title
    except:
        product_dict['Product_Title']="No Title"
    product_details=extract_product_about_details(main_driver)
    product_dict['Product_Detail']=product_details
    try:
        average_review=main_driver.find_element(By.XPATH,"//div[@id='averageCustomerReviews']").text
        product_dict['Average_Review']=average_review
    except:
        product_dict['Average_Review']=None
    color=extract_colors(main_driver)
    product_dict["Color"]=color
    reviews=extract_reviews(main_driver)
    product_dict['Reviews']=reviews
    return product_dict,product_title


def save_to_pc(product_list,category_name,inner_sub,inner_inner_sub):
    if not os.path.exists(category_name):
        os.makedirs(category_name)
    path = os.path.join(category_name,inner_sub)
    if not os.path.exists(path):
        os.makedirs(path)
    path1 = os.path.join(path,inner_inner_sub)
    try:
        with open(f"{path1}.json", "w") as json_file:
            json.dump(product_list, json_file, indent=4)
        print("Successfuly saved", path1)
    except TypeError as e:
        problematic_elements = []
        for item in product_list:
            if isinstance(item, WebElement):
                problematic_elements.append(item)
        print("The following elements are causing serialization errors:")
        for elem in problematic_elements:
            print(elem)

def save_to_pc1(product_list,category_name,inner_sub,inner_inner_sub,title):
    if not os.path.exists(category_name):
        os.makedirs(category_name)
    path = os.path.join(category_name,inner_sub)
    if not os.path.exists(path):
        os.makedirs(path)
    path1 = os.path.join(path,inner_inner_sub)
    if not os.path.exists(path1):
        os.makedirs(path1)
    pattern = r'[^\w\s\-.]'
    title=re.sub(pattern, '', title)
    path1 = os.path.join(path1,title)
    try:
        with open(f"{path1}.json", "w") as json_file:
            json.dump(product_list, json_file, indent=4)
        print("Successfuly saved", path1)
    except TypeError as e:
        return 
        problematic_elements = []
        for item in product_list:
            if isinstance(item, WebElement):
                problematic_elements.append(item)
        print("The following elements are causing serialization errors:")
        for elem in problematic_elements:
            print(elem)

from selenium.webdriver.remote.webelement import WebElement
def extract_products(main_driver,category_name,inner_sub,inner_inner_sub):
    product_list=[]
    k=0
    checker=True
    while True:
        links=[]
        products=main_driver.find_elements(By.XPATH,'//h2[@class="a-size-mini a-spacing-none a-color-base s-line-clamp-4"]')
        for l in products:
            try:
                link2 = l.find_element(By.TAG_NAME, 'a').get_attribute('href')
                links.append(link2)
            except:
                continue
        print(len(links))
        for link2 in links:
            if k==100:
                checker=False
                break
            product_dict={}
            product_list_indi=[]
            product_dict['Category']=category_name
            product_dict['Sub_Category']=inner_sub
            product_dict['Sub_Sub_Category']=inner_inner_sub
            product_dict['Product_link']=link2
            #p=product.find_element(By.XPATH,'//h2[@class="a-size-mini a-spacing-none a-color-base s-line-clamp-4"]')
            #print(product.text)
            main_driver.execute_script("window.open(arguments[0], '_blank');", link2)
            random_sleep(3, 5)
            main_driver.switch_to.window(main_driver.window_handles[-1])
            product_dict,title=extract_product_details(main_driver,product_dict)
            product_list.append(product_dict)
            product_list_indi.append(product_dict)
            save_to_pc1(product_list_indi,category_name,inner_sub,inner_inner_sub,title)
            random_sleep(3, 5)
            main_driver.close()
            main_driver.switch_to.window(main_driver.window_handles[-1])
            random_sleep(3, 5)
            k=k+1
        if checker==False:
            break
        try:
            print("Next Page")
            next_page=main_driver.find_element(By.XPATH,"//a[@aria-label='Go to page 2']")
            next_page.click()
            random_sleep(5, 8)
            continue
        except:
            break

    save_to_pc(product_list,category_name,inner_sub,inner_inner_sub)


def setup_webdriver(proxy, port):
    l1 = subprocess.Popen([os.getenv("chrome_path"), f'{os.getenv("remote_debugger")}{os.getenv("port1")}', f'{os.getenv("user_dir")}{os.getenv("chrome1")}'])
    web='https://www.amazon.com/s?i=fashion-mens-intl-ship&bbn=16225019011&rh=n%3A7141123011%2Cn%3A16225019011%2Cn%3A7147441011&dc&qid=1708163067&ref=sr_pg_1'
    web_driver_path = os.getenv("web_driver_path")
    service = Service(executable_path=web_driver_path)
    options = Options()
    options.add_argument("--headless")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    options.add_experimental_option("debuggerAddress", f'localhost:{port}')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument(f"--proxy-server={proxy}")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(web)
    return driver


import random

main_driver = setup_webdriver(os.getenv("proxy1"), os.getenv("port1"))

random_sleep(5, 8)


category=main_driver.find_element(By.XPATH,'//div[@id="departments"]')
category_name=category.find_element(By.XPATH,'''//li[contains(@class, 'a-spacing-micro') and contains(@class, 's-navigation-indent-1')]''').text
print(category_name)
u=0
sub_category=category.find_elements(By.XPATH,'//li[contains(@id, "n/") and contains(@class, "a-spacing-micro") and contains(@class, "s-navigation-indent-2")]/span[contains(@class, "a-list-item")]')

for sub in sub_category:
    
    inner_sub=sub.text
    link = sub.find_element(By.TAG_NAME, 'a').get_attribute('href')
    main_driver.execute_script("window.open(arguments[0], '_blank');", link)
    main_driver.switch_to.window(main_driver.window_handles[-1])
    random_sleep(3, 5)
    
    dep = main_driver.find_element(By.XPATH, '//div[@id="departments"]')
    sub_category_list = dep.find_elements(By.XPATH, '//li[contains(@id, "n/") and contains(@class, "a-spacing-micro") and contains(@class, "s-navigation-indent-2")]/span[contains(@class, "a-list-item")]')
    # k=0
    for sub_cat in sub_category_list:
        # if k==1:
        #     break
        inner_inner_sub=sub_cat.text
        link1 = sub_cat.find_element(By.TAG_NAME, 'a').get_attribute('href')
        main_driver.execute_script("window.open(arguments[0], '_blank');", link1)
        main_driver.switch_to.window(main_driver.window_handles[-1])
        random_sleep(3, 5)
        extract_products(main_driver,category_name,inner_sub,inner_inner_sub)
        main_driver.close()
        main_driver.switch_to.window(main_driver.window_handles[-1])
        random_sleep(20, 40)
        #k=k+1
    main_driver.close()
    main_driver.switch_to.window(main_driver.window_handles[-1])
    random_sleep(30,60 )



    