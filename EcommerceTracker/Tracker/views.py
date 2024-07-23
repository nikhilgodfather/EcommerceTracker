from django.shortcuts import render , get_object_or_404
from django.http import JsonResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException, InvalidArgumentException  ,NoSuchElementException
import time
import json
from .models import TrackData
import requests
from bs4 import BeautifulSoup
import threading
from django.db import connection
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def home(request):
    if request.method == 'GET':
        return render(request, 'Form.html')

    elif request.method == "POST":
        NameUrl = request.POST.get('NameUrl')
        url = request.POST.get('url')
        email = request.POST.get('email')
        ExpectedPrice = request.POST.get('price')

        if not NameUrl:
            error_name_url = {
                "error": "Please Select a Platform"
            }
            return render(request, "Form.html", {'ErrorNameUrl': error_name_url})

        context = {}
        if NameUrl == 'Amazon':
            try:
                options = Options()
                options.add_argument('--headless')
                driver = webdriver.Firefox(options=options)
                driver.get(url)

                title = driver.find_element(By.XPATH, '//*[@id="productTitle"]').text.replace("'", "")

                try:
                    price = driver.find_element(By.XPATH, '//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[3]/span[2]').text
                except NoSuchElementException:
                    price = driver.find_element(By.XPATH, '//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[2]/span[2]').text

                image_element = driver.find_element(By.XPATH, '//*[@id="landingImage"]')
                image_src = image_element.get_attribute('src')

                if not ExpectedPrice:
                    ExpectedPrice = price

                if price and title and image_src:
                    context = {
                        "NameUrl": NameUrl,
                        "price": price,
                        "title": title,
                        "imageSrc": image_src,
                        "url": url,
                        "email": email,
                        "ExpectedPrice": ExpectedPrice
                    }
                else:
                    error_message = {
                        "error": "Invalid URL!"
                    }
                    driver.quit()
                    return render(request, "Form.html", {'errorMessage': error_message})

            except Exception as e:
                print(f"Error: {e}")
                error_message = {
                    "error": "Invalid URL!"
                }
                driver.quit()
                return render(request, "Form.html", {'errorMessage': error_message})
            finally:
                driver.quit()

        elif NameUrl == 'Flipkart':
            try:
                response = requests.get(url)
                soap = BeautifulSoup(response.text, 'html.parser')

                mainClass = soap.find('div' , class_='C7fEHH')
                title = mainClass.find('h1' , class_='_6EBuvT').text.strip()
                PriceContainer = mainClass.find('div' , class_='x+7QT1')
                PriceBlock = PriceContainer.find('div' , class_='UOCQB1')
                PriceMain = PriceBlock.find('div' , class_='hl05eU')
                price = PriceMain.find('div' , class_='Nx9bqj CxhGGd').text.strip()
                img_element = soap.find('img', class_='_0DkuPH')
                if img_element:
                    image_src = img_element.get('src')

                if not ExpectedPrice:
                    ExpectedPrice = price

                if title and price and image_src:
                    context = {
                        "NameUrl": NameUrl,
                        "price": price,
                        "title": title,
                        "imageSrc": image_src,
                        "url": url,
                        "email": email,
                        "ExpectedPrice": ExpectedPrice
                    }
                else:
                    error_message = {
                        "error": "Invalid URL!"
                    }
                    return render(request, "Form.html", {'errorMessage': error_message})

            except Exception as e:
                print(f"Error: {e}")
                error_message = {
                    "error": "Invalid URL!"
                }
                return render(request, "Form.html", {'errorMessage': error_message})

        return render(request, "Form.html", {'context': context})
            

def Track(request):
    if request.method == 'POST':
        context_json = request.POST.get('context')
        if context_json:
            # Fix common issues with escaped characters in the JSON string
            context_fixed = context_json.replace("'", '"')
            context_fixed = context_fixed.replace('\\', '\\\\')  # Properly escape backslashes
            
            try:
                # Deserialize JSON data into a Python dictionary
                context = json.loads(context_fixed)
                
                # Save context data to the database
                track_Data = TrackData.objects.create(
                    Name_Url=context.get('NameUrl'),
                    Item_Price=context.get('price'),
                    Title=context.get('title'),
                    Item_Image_url=context.get('imageSrc'),
                    Item_Url=context.get('url'),
                    Email=context.get('email'),
                    Expected_Price=context.get('ExpectedPrice')
                )
                track_Data.save()
                
                # Render the template with context data
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
                return render(request, 'Form.html', {'error': f'Error decoding JSON: {e}', 'context': context_json})
        else:
            print("No context data received")
            return render(request, 'Form.html', {'error': 'No context data received'})
    
    # Retrieve all entries from the database
    track_data_entries = TrackData.objects.all()
    # Pass the entries to the template
    context = {'track_data_entries': track_data_entries}
    return render(request, 'TrackTable.html', context)

def delete(request , Id):
   if request.method == 'DELETE':
        track_data = get_object_or_404(TrackData, pk=Id)
        track_data.delete()
        return JsonResponse({'message': 'TrackData deleted successfully'}, status=200)
   return JsonResponse({'error': 'Invalid request'}, status=400)
        
thread_running = False
def track_data_entries():
    global thread_running
    while True:
        try:
            # Ensure the database connection is alive
            connection.ensure_connection()

            # Fetch all entries from TrackData
            entries = TrackData.objects.all()
            for entry in entries:
                if entry.Name_Url == 'Flipkart':
                    response = requests.get(entry.Item_Url)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        main_class = soup.find('div', class_='C7fEHH')
                        if main_class:
                            price_container = main_class.find('div', class_='x+7QT1')
                            if price_container:
                                price_block = price_container.find('div', class_='UOCQB1')
                                if price_block:
                                    price_main = price_block.find('div', class_='hl05eU')
                                    if price_main:
                                        price_text = price_main.find('div', class_='Nx9bqj CxhGGd').text.strip()
                                        price = int(price_text.replace('₹', '').replace(',', ''))  # Convert price text to integer
                                        
                                        item_price = int(entry.Item_Price.replace('₹', '').replace(',', ''))
                                        expected_price = int(entry.Expected_Price.replace('₹', '').replace(',', ''))

                                        if price != item_price:
                                            entry.Item_Price = f'₹{price}'
                                            entry.save(update_fields=['Item_Price'])

                                        if price <= expected_price:
                                            Email(entry.Email, entry.Item_Image_url, price, entry.Expected_Price, entry.Item_Url, entry.Title)
                    else:
                        entry.Name_Url = 'OUT OF STOCK!'
                        entry.save(update_fields=['Name_Url'])
                elif entry.Name_Url == 'Amazon':
                    try:
                        options = Options()
                        options.add_argument('--headless')
                        driver = webdriver.Firefox(options=options)
                        driver.get(entry.Item_Url)
                        try:
                            price = driver.find_element(By.XPATH, '//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[3]/span[2]').text
                        except NoSuchElementException:
                            price = driver.find_element(By.XPATH, '//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[2]/span[2]').text
                        except NoSuchElementException:
                            price = entry.Item_Price  
                        Current_price = int(price.replace('₹', '').replace(',', ''))   
                        item_price = int(entry.Item_Price.replace('₹', '').replace(',', ''))
                        expected_price = int(entry.Expected_Price.replace('₹', '').replace(',', ''))
                        if Current_price != item_price:
                          entry.Item_Price = f'₹{price}'
                          entry.save(update_fields=['Item_Price'])
                        if Current_price <= expected_price:
                            Email(entry.Email , entry.Item_Image_url , Current_price , entry.Expected_Price , entry.Item_Url , entry.Title)
                    except Exception as e:
                        print(f"Error: {e}")
                        driver.quit()
                    finally:
                        driver.quit()
                                
        except Exception as e:
            print(f"Error occurred: {e}")
                

        # Wait for one hour
        time.sleep(3600)

def start_background_task():
    global thread_running
    if not thread_running:
        # Create and start a background thread
        thread = threading.Thread(target=track_data_entries, daemon=True)
        thread.start()
        thread_running = True
    else:
        print("Thread is already running.")
    
    
def Email(email, image_url, item_price, expected_price, item_url, title):
    html = f'''
    <html>
    <head>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
        <style>
            .card-custom {{
                border: 2px solid #007bff;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                margin: 20px;
                max-width: 400px;
                padding: 20px;
            }}
            .card-custom img {{
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }}
            .card-custom .card-body {{
                background-color: #f8f9fa;
            }}
            .card-custom .card-title {{
                font-size: 1.25rem;
                font-weight: bold;
            }}
            .card-custom .card-text {{
                font-size: 1rem;
                margin-bottom: 10px;
            }}
            .card-custom .btn-primary {{
                background-color: #007bff;
                border-color: #007bff;
                border-radius: 5px;
                padding: 10px;
                
            }}
            .btn-primary {{
                color: white;
            }}
        </style>
    </head>
    <body>
        <div class="card card-custom">
            <img class="card-img-top" src="{image_url}" alt="Card image cap">
            <div class="card-body">
                <h5 class="card-title">{title}</h5>
                <p class="card-text">Your Tracking Item Price has dropped to the Current Price: <b>{item_price}</b>, which matches or is below your Expected Price: <b>{expected_price}</b>.</p>
                <a href="{item_url}" class="btn btn-primary">View Item</a>
            </div>
        </div>
        <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/popper.js@1.12.9/dist/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
    </body>
    </html>
    '''

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = 'nikhilagg711@gmail.com'
    msg['To'] = email
    msg['Subject'] = 'Price Drop Alert!'

    msg.attach(MIMEText(html, 'html'))

    # Send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('nikhilagg711@gmail.com', 'xvqz flzg hnmz zadt')
        server.sendmail('nikhilagg711@gmail.com', email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()
        
start_background_task()