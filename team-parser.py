import json
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
import logging
import concurrent.futures
import time
import random
from PIL import Image, UnidentifiedImageError
from collections import Counter
import cv2
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

base_url = "https://dota2.ru/esport/"
uploads_dir = "uploads"
pattern = r"Команда\s+|\s+по Dota 2"

if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)
    
session = requests.Session()

def fetch_page_data(url):
    try:
        logging.info(f'Fetching data from {url}')
        response = session.get(url)
        response.raise_for_status()
        src = response.content
        soup = BeautifulSoup(src, 'lxml')
        logging.info(f'Successfully fetched data from {url}')
        time.sleep(random.uniform(0.5, 1.5))
        return soup
    except requests.exceptions.RequestException as e:
        logging.error(f'Failed to fetch data from {url}: {e}')
        return None

def remove_background_opencv(image_path):
    try:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour = max(contours, key=cv2.contourArea)
        mask = np.zeros_like(gray)
        cv2.drawContours(mask, [contour], -1, 255, -1)
        masked_img = cv2.bitwise_and(img, img, mask=mask)
        
        # Save the masked image
        output_path = image_path.rsplit('.', 1)[0] + "_no_bg.png"
        cv2.imwrite(output_path, masked_img)
        
        logging.info(f'Background removed using OpenCV for {image_path}')
        return output_path
    except Exception as e:
        logging.error(f'Failed to remove background using OpenCV for {image_path}: {e}')
        return None


def parse_page_players(soup, uploads_dir):
    table = soup.find('table')
    page_player_info = []
    player_base_url = 'https://dota2.ru/esport/player/'
    player_dir = os.path.join(uploads_dir, 'player')
    os.makedirs(player_dir, exist_ok=True)
    table_rows = table.find_all('tr')

    for row in table_rows:
        player_fullname = ''
        player_org_name = ''
        player_position_name = ''
        player_country_name = ''
        player_birth_date = ''
        player_nick = ''
        player_image_name = ''
        player_image_dominant_color = ''
        cols = row.find_all('td')
        
        if len(cols) > 0:
            player_div = cols[0].find('div')
            player_link = player_div.find('a')['href']
            player_url = urljoin(player_base_url, player_link)
           
            player_soup = fetch_page_data(player_url)
            if player_soup:
                player_full_info = player_soup.find('table')
                player_nickname = player_soup.find('h1', class_="title-global").text.strip()
                pattern_nickname = r'Игрок ([A-Za-z0-9\-\._]+) по Dota 2'

                if player_nickname:
                    match = re.search(pattern_nickname, player_nickname)
                    if match:
                        player_nick = match.group(1)
                        logging.info(f'Nickname extracted for player: {player_nick}')
                
                player_full_info_blocks = player_full_info.find_all('tr')
                for player in player_full_info_blocks:
                    player_name = player.find(id='firstName')
                    player_surname = player.find(id='lastName')
                    if player_name is not None and player_surname is not None:
                        player_fullname = player_name.text.strip() + " " + player_surname.text.strip()
                    player_org = player.find(id="playerTeam")
                    if player_org is not None:
                        player_org_name = player_org.text.strip()
                    player_position = player.find(id="playerPosition")
                    if player_position is not None:
                        player_position_name = player_position.text.strip()
                    player_country = player.find(id="country")
                    if player_country is not None:
                        player_country_name = player_country.text.strip()
                    player_date_birth = player.find(id='playerBirthday')
                    if player_date_birth:
                        player_birth_date = player_date_birth.text.strip()

            
                player_image = player_soup.find('img', class_="img-120")
                if player_image:
                    player_image_url = player_image.get('src')
                    player_image_filename = os.path.basename(urlparse(player_image_url).path)
                    player_image_filepath = os.path.join(player_dir, player_image_filename)
                    player_image_name = player_image_filename
                    player_image_response = requests.get(f"https://dota2.ru/{player_image_url}")
                    with open(player_image_filepath, 'wb') as img_file:
                        img_file.write(player_image_response.content)
                        logging.info(f'Image downloaded for player: {player_image_filename}')
                    # Convert to PNG if image is in .webp format
                    if player_image_filename.endswith('.webp'):
                        player_image_filepath = convert_image_to_png(player_image_filepath)
                        if player_image_filepath:  # Check if conversion was successful
                            player_image_name = os.path.basename(player_image_filepath)
                        else:
                            player_image_name = None
                    # Remove background from player image using OpenCV
                    if player_image_filepath:  # Check if file path is valid
                        player_image_no_bg_path = remove_background_opencv(player_image_filepath)
                        if player_image_no_bg_path:
                            player_image_name = os.path.basename(player_image_no_bg_path)
                        else:
                            player_image_name = None
                    # Get dominant color for player image
                    if player_image_no_bg_path:  # Check if file path is valid
                        player_image_dominant_color = get_dominant_color(player_image_no_bg_path)
            
            page_player_info.append({
                "player_fullname": player_fullname,
                "player_org_name": player_org_name,
                "player_position_name": player_position_name,
                "player_country_name": player_country_name,
                "player_birth_date": player_birth_date,
                "player_nick": player_nick,
                "player_image_name" : player_image_name,
                "player_image_dominant_color": player_image_dominant_color
            })
    return page_player_info



def parse_page_teams(soup, uploads_dir):
    flags_dir = os.path.join(uploads_dir, 'flags')
    teams_dir = os.path.join(uploads_dir, 'teams')
    os.makedirs(flags_dir, exist_ok=True)
    os.makedirs(teams_dir, exist_ok=True)
    table_rows = soup.find('table').find_all('tr', class_='title')
    page_org_info = []
    team_base_url = 'https://dota2.ru/esport/team/'
    
    for row in table_rows:
        country_text = ""
        flag_filename = ""
        flag_dominant_color = ""
        location_text = ""
        world_rating = 0
        earned = 0
        org_name  = ""
        org_image = ""
        org_image_dominant_color = ""
        current_href = row.find('a').get('href')
        team_url = urljoin(team_base_url, current_href)
        
        team_soup = fetch_page_data(team_url)
        if team_soup:
            team_org_name = team_soup.find('h1', class_="title-global").text.strip()
            if team_org_name:
                cleaned_team_org_name = re.sub(pattern, "", team_org_name)
                org_name = cleaned_team_org_name
            
            team_org_image = team_soup.find('img', class_="cybersport-players-player__img")
            
            if team_org_image:
                team_org_image_url = team_org_image['src']
                team_org_image_filename = os.path.basename(urlparse(team_org_image_url).path)
                team_org_image_filepath = os.path.join(teams_dir, team_org_image_filename)
                org_image = team_org_image_filename
                team_org_image_response = requests.get(f"https://dota2.ru/{team_org_image_url}")
                with open(team_org_image_filepath, 'wb') as img_file:
                    img_file.write(team_org_image_response.content)
                    logging.info(f'Image downloaded for team: {team_org_image_filename}')
                # Convert to PNG if image is in .webp format
                if team_org_image_filename.endswith('.webp'):
                    team_org_image_filepath = convert_image_to_png(team_org_image_filepath)
                    if team_org_image_filepath:  # Check if conversion was successful
                        org_image = os.path.basename(team_org_image_filepath)
                    else:
                        org_image = None
                # Remove background from team image using OpenCV
                if team_org_image_filepath:  # Check if file path is valid
                    team_image_no_bg_path = remove_background_opencv(team_org_image_filepath)
                    if team_image_no_bg_path:
                        org_image = os.path.basename(team_image_no_bg_path)
                    else:
                        org_image = None
                # Get dominant color for team image
                if team_image_no_bg_path:  # Check if file path is valid
                    org_image_dominant_color = get_dominant_color(team_image_no_bg_path)
            
            team_info_table = team_soup.find('table', class_="cybersport-players-player__table")
            if team_info_table:
                team_info = team_info_table.find_all('tr')

                if len(team_info) > 0:
                    team_info_country = team_info[0].find(id="country")
                    if team_info_country:
                        country_text = team_info_country.text.strip()
                        team_info_country_img = team_info_country.find('img')
                        if team_info_country_img:
                            team_info_country_img_url = team_info_country_img['src']
                            flag_filename = os.path.basename(urlparse(team_info_country_img_url).path)
                            team_info_country_img_filepath = os.path.join(flags_dir, flag_filename)
                            team_info_country_img_response = requests.get(f"https://dota2.ru/{team_info_country_img_url}")
                            with open(team_info_country_img_filepath, 'wb') as img_file:
                                img_file.write(team_info_country_img_response.content)
                            logging.info(f'Flag downloaded for team: {flag_filename}')
                            # Convert to PNG if image is in .webp format
                            if flag_filename.endswith('.webp'):
                                team_info_country_img_filepath = convert_image_to_png(team_info_country_img_filepath)
                                if team_info_country_img_filepath:  # Check if conversion was
                                    flag_filename = os.path.basename(team_info_country_img_filepath)
                            else:
                                flag_filename = None
                            # Get dominant color for flag
                            if team_info_country_img_filepath:  # Check if file path is valid
                                flag_dominant_color = get_dominant_color(team_info_country_img_filepath)

                if len(team_info) > 1:
                    team_info_location = team_info[1].find(id="teamLocation")
                    if team_info_location:
                        location_text = team_info_location.text.strip()
                if len(team_info) > 2:
                    team_info_rating = team_info[2].find_all('span')
                    if len(team_info_rating) > 2:
                        world_rating = team_info_rating[2].text.strip()
                if len(team_info) > 3:
                    team_info_earned_elem = team_info[3].find(id="teamEarn")
                    if team_info_earned_elem:
                        team_info_earned = team_info_earned_elem.text.strip()
                        earned = team_info_earned
                    else:
                        team_info_earned = ""
                        earned = ""
            
            page_org_info.append({
                "country_text": country_text,
                "flag": flag_filename,
                "flag_dominant_color": flag_dominant_color,
                "location": location_text,
                "world_rating": world_rating,
                "earned": earned,
                "org_name": org_name,
                "org_image" : org_image,
                "org_image_dominant_color": org_image_dominant_color
            })

    return page_org_info

def get_total_pages_teams(soup):
    pagination = soup.find('ul', class_="pagination").find('li', class_="pagination__item pagination__link--right").text.strip()
    return int(pagination)

def get_total_pages_players(soup):
    pagination = soup.find('ul', class_="pagination").find('li', class_="pagination__item pagination__link--right").text.strip()
    return int(pagination)

def get_dominant_color(image_path, k=1):
    """
    Find the dominant color in an image.
    :param image_path: Path to the image file
    :param k: Number of dominant colors to return (k=1 means the single most dominant color)
    :return: List of k dominant colors in hexadecimal format
    """
    try:
        image = Image.open(image_path)
        image = image.convert('RGB')  # Ensure image is in RGB format
        image = image.resize((150, 150))  # Resize to reduce the number of pixels
        pixels = list(image.getdata())
        most_common_colors = Counter(pixels).most_common(k)
        dominant_colors = [f'#{r:02x}{g:02x}{b:02x}' for (r, g, b), _ in most_common_colors]
        return dominant_colors[0]
    except UnidentifiedImageError:
        logging.error(f'Cannot identify image file {image_path}')
        return None

def convert_image_to_png(image_path):
    """
    Convert an image to PNG format.
    :param image_path: Path to the original image file
    :return: Path to the converted PNG image file
    """
    try:
        image = Image.open(image_path)
        png_image_path = image_path.rsplit('.', 1)[0] + '.png'
        image.save(png_image_path, 'PNG')
        logging.info(f'Converted {image_path} to {png_image_path}')
        return png_image_path
    except UnidentifiedImageError:
        logging.error(f'Cannot identify image file {image_path}')
        return None

org_info = {"teams": [], "players": []}  

def fetch_and_parse_teams(url):
    soup = fetch_page_data(url)
    if soup:
        return parse_page_teams(soup, uploads_dir)
    else:
        return []

def fetch_and_parse_players(url):
    soup = fetch_page_data(url)
    if soup:
        return parse_page_players(soup, uploads_dir)
    else:
        return []

try:
    soup_teams = fetch_page_data(base_url + '/teams')
    total_pages_teams = get_total_pages_teams(soup_teams)

    logging.info(f'Starting parallel processing for teams pages...')
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        team_urls = [f"{base_url}/teams?page={page_num}" for page_num in range(1, 1 + 1)]
        team_results = executor.map(fetch_and_parse_teams, team_urls)
        for result in team_results:
            org_info["teams"].extend(result)
    
    logging.info(f'Finished processing teams pages.')

    soup_players = fetch_page_data(base_url + '/players')
    total_pages_players = get_total_pages_players(soup_players)
    
    logging.info(f'Starting parallel processing for players pages...')
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        player_urls = [f"{base_url}/players?page={page_num}" for page_num in range(1, 1 + 1)]
        player_results = executor.map(fetch_and_parse_players, player_urls)
        for result in player_results:
            org_info["players"].extend(result)
    
    logging.info(f'Finished processing players pages.')

    filename = "data.json"
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(org_info, file, ensure_ascii=False, indent=4)

    logging.info(f'Data with dominant colors successfully written to {filename}')

except Exception as e:
    logging.error(f'An error occurred: {str(e)}')
