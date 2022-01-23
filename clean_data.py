''''
Module created for specifically cleaning data scraped data from winemag.com
'''
import os
import json
import pickle
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm


class DataCleaner():
    '''
    class created for parsing wine data
    '''
    def __init__(self, file_path, file_name):
        self.file_name = file_name
        self.file_path = file_path
        with open(self.file_path+self.file_name, 'r', encoding='utf-8') as wine_file:
            self.html_file = wine_file.read()
        self.soup = BeautifulSoup(self.html_file, 'html.parser')
        self.primary = self.soup.find(class_="primary-info").find_all('li')
        self.data_pure = self.soup.find_all(type="application/ld+json")[1]
        self.data_json = json.loads(str(self.data_pure).replace(\
            '<script type="application/ld+json">', '').replace('\n', '').replace(\
                '</script>', ''))


    def get_wine_name(self):
        '''
        Retrieves name of wine
        '''
        if self.data_json['review']['name'] is not None:
            wine_name = self.data_json['review']['name']
        else:
            wine_name = np.nan
        return wine_name

    def get_winery_name(self, wine_dict):
        '''
        Retrieves name of winery
        '''
        for list_item in self.primary:
            if list_item.find(class_="info-label medium-7 columns").text.strip() == 'Winery':
                winery = list_item.find(class_="info medium-9 columns").text.strip()
            return winery
        if len(wine_dict['winery']) != len(wine_dict['wine'])-1:
            winery = np.nan
            return winery

    def get_designation(self, wine_dict):
        '''
        Retrieves wine designation. If none is found checks designation list length to ensure
        it is the same length as the other lists.
        '''
        for list_item in self.primary:
            if list_item.find(class_="info-label medium-7 columns").text.strip() == 'Designation':
                designation = list_item.find(class_="info medium-9 columns").text.strip()
            return designation
        if len(wine_dict['designation']) != len(wine_dict['wine'])-1:
            designation=np.nan
            return designation

    def get_category(self):
        '''
        Retrieves wine category
        '''
        if self.data_json['category'] is not None:
            category = self.data_json['category']
        else:
            category = np.nan
        return category

    def get_varietal(self, wine_dict):
        '''
        Retrieves wine varietal. If none is found checks varietal list length to ensure
        it is the same length as the other lists.
        '''
        for info in self.soup.find_all(class_='info medium-9 columns'):
            if 'varietal' in str(info):
                varietal = info.text.strip()
            return varietal
        if len(wine_dict['varietal']) != len(wine_dict['wine'])-1:
            varietal = np.nan
            return varietal

    def get_appellation(self, wine_dict):
        '''
        Retrieves appellation designation. If none is found checks appellation
        list length to ensure it is the same length as the other lists.
        '''
        data_points =self.soup.find_all(class_='info medium-9 columns')
        for data in data_points:
            if 'region' in str(data):
                appellation = data.text.strip()
            return appellation
        if len(wine_dict['appellation']) != len(wine_dict['wine'])-1:
            appellation = np.nan
            return appellation

    def get_alcohol_content(self, wine_dict):
        '''
        Retrieves wine alcohol content. If none is found checks alcohol list
        length to ensure it is the same length as the other lists.
        '''
        secondary = self.soup.find(class_="secondary-info").find_all('li')
        for list_item in secondary:
            if list_item.find(class_="info-label small-7 columns").text.strip() == 'Alcohol':
                alcohol = list_item.find(class_="info small-9 columns").text.strip()
            return alcohol
        if len(wine_dict['alcohol']) != len(wine_dict['wine'])-1:
            alcohol=np.nan
            return alcohol

    def get_price(self):
        '''
        Retrieves price of wine
        '''
        if self.soup.find(class_="buy-now__link").parent.text.replace(',Buy Now', '') is not None:
            price = self.soup.find(class_="buy-now__link").parent.text.replace(',Buy Now', '')
        else:
            price = np.nan
        return price

    def get_rating(self):
        '''
        Retrieves wine rating
        '''
        if self.data_json['review']['reviewRating']['ratingValue'] is not None:
            rating = self.data_json['review']['reviewRating']['ratingValue']
        else:
            rating = np.nan
        return rating

    def get_reviewer(self):
        '''
        Retrieves wine reviewer name
        '''
        if self.data_json['review']['author']['name'] is not None:
            reviewer = self.data_json['review']['author']['name']
        else:
            reviewer = np.nan
        return reviewer

    def get_review(self):
        '''
        Retrieves wine review
        '''
        if self.data_json['review']['reviewBody'] is not None:
            review = self.data_json['review']['reviewBody']
        else:
            review = np.nan
        return review


if __name__ == "__main__":

    wines_dict = {'wine':[], 'winery':[], 'category':[], 'designation':[], 'varietal':[],
                 'appellation':[], 'alcohol':[], 'price':[], 'rating':[],'reviewer':[],
                 'review':[]}
    bad_files = []
    HTML_FILE_PATH = './data/wine_html_example/'
    wine_files = os.listdir(HTML_FILE_PATH)
    for wine in tqdm(wine_files):
        try:
            clean_data = DataCleaner(HTML_FILE_PATH, wine)
            wines_dict['wine'].append(clean_data.get_wine_name())
            wines_dict['winery'].append(clean_data.get_winery_name(wines_dict))
            wines_dict['designation'].append(clean_data.get_designation(wines_dict))
            wines_dict['varietal'].append(clean_data.get_varietal(wines_dict))
            wines_dict['category'].append(clean_data.get_category())
            wines_dict['price'].append(clean_data.get_price())
            wines_dict['appellation'].append(clean_data.get_appellation(wines_dict))
            wines_dict['alcohol'].append(clean_data.get_alcohol_content(wines_dict))
            wines_dict['rating'].append(clean_data.get_rating())
            wines_dict['reviewer'].append(clean_data.get_reviewer())
            wines_dict['review'].append(clean_data.get_review())
        except AttributeError:
            bad_files.append(wine)


    df_wine = pd.DataFrame(wines_dict)
    df_wine.to_csv('./data/wine.csv', index=False)

    with open('./bad_files/bad_files.pkl', 'wb') as fp:
        pickle.dump(bad_files, fp)

    print(len(bad_files))
    