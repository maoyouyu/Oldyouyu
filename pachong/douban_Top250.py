#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author : Dong-Qing 
# Time : 2018/3/22

from bs4 import BeautifulSoup

import requests

def download_page(url):
    return requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
    }).content

def parse_html(html):
    soup = BeautifulSoup(html)
    movie_list_soup = soup.find('ol', attrs={'class': 'grid_view'})

    movie_name_list = []

    for movie_li in movie_list_soup.find_all('li'):
        detail = movie_li.find('div', attrs={'class': 'hd'})
        movie_name = detail.find('span', attrs={'class': 'title'}).getText()

        movie_name_list.append(movie_name)

    next_page = soup.find('span', attrs={'class': 'next'}).find('a')
    if next_page:
        return movie_name_list, url + next_page['href']
    return movie_name_list, None

def main(url):
    movies_list = []
    while url:
        html = download_page(url)
        movies, url = parse_html(html)
        movies_list.extend(movies)

    return movies_list



if __name__ == '__main__':

    url = 'https://movie.douban.com/top250'
    movie_name_list = main(url)
