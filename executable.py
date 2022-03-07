#emsi bg job board executable

import requests
from bs4 import BeautifulSoup
import pandas as pd
from seleniumwire import webdriver
import ast
import os

url = 'https://www.economicmodeling.com/open-positions/'

headers = {
    'User-Agent':'not-suspicious-bot'
}

job_board_html = requests.get(url, headers=headers)

#create a new instance of chrome driver with the appropriate options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--ignore-certificate-errors-spki-list')
chrome_options.add_argument('--ignore-ssl-errors')

#have to put your local path to the driver!
driver = webdriver.Chrome(executable_path=r"C:\Users\Admin\Documents\Programming\CHROME DRIVER\chromedriver.exe", options=chrome_options)


#grab the emsi page
driver.get(url)

#create a blank array to store responses
requests_array = []

#grab requests from requests
for request in driver.requests:
    if request.response:
        requests_array.append(request.url)

requests_df = pd.DataFrame(requests_array)
api_df = requests_df.loc[requests_df[0].str.contains('api', case=False)].reset_index()

for api in api_df[0]:
    print(api)
    print()

for api in api_df[0][2:]:
    try: 
        print(api)
        print(pd.DataFrame(requests.get(api, headers=headers).json()))
        print()
    except Exception as e:
        print(e)
        print()

job_api = pd.DataFrame(requests.get('https://api.lever.co/v0/postings/economicmodeling?group=team&mode=json', headers=headers).json())
job_api = job_api.rename(columns={'title':'category'}) #the titles didn't really seem like job titles, more like categories
category_array = []

for index, row in job_api.iterrows():
    path = f"{row['category']}.csv"
    pd.DataFrame(row['postings']).to_csv(path, index=False)
    category_array.append(path)

final_array = []
for category in category_array:
    #these are the columns I want from the json output
    final_df = pd.read_csv(category, index_col=None)[['text', 'descriptionPlain', 'categories', 'hostedUrl']]

    final_df['categories'] = final_df['categories'].apply(lambda x: ast.literal_eval(x).get('location'))
    #categories column itself is json, but isn't formatted; ast is used to help format and interpret as json

    final_df.rename(columns={'categories':'location', 'text':'job_title', 'descriptionPlain':'description'}, inplace=True)
    final_df['department'] = category.replace('.csv', '')
    final_array.append(final_df)
    os.remove(category)
pd.concat(final_array).reset_index(drop=True).to_csv('job_listings.csv', index=False)

print()
print('All done!')