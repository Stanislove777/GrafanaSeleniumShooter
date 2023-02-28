from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time
import json
import argparse
import os
import logging

# Create args
def create_args():
    parser = argparse.ArgumentParser(description='GrafanaScreenShooter')
    parser.add_argument('--dashboard', 
        type=str, 
        help='Dashboard name where to get charts from')
    parser.add_argument('--rows', 
        nargs='*', 
        help='Rows to which the required panels belong. Value can be empty then all dashboard charts are saved')
    parser.add_argument('--storage_dir', 
        type=str, 
        help='Directory where pictures (and their folders) are stored')
    parser.add_argument('--host', 
        type=str, 
        help='Server where Grafana is installed')
    parser.add_argument('--username', 
        type=str, 
        help='Grafana login username')
    parser.add_argument('--password', 
        type=str, 
        help='Grafana login password')
    parser.add_argument('--org_id', 
        type=str, 
        help='OrgId for URL panels')
    parser.add_argument('--time_range_start', 
        type=str, 
        help='Start of the time period')
    parser.add_argument('--time_range_end', 
        type=str, 
        help='End of the time period')
    parser.add_argument('--drv_path', 
        type=str, 
        help='Path for chrome driver')
    return parser.parse_args()

# Login Grafana
def login(driver, args):
    driver.get(args.host + '/login')
    driver.find_element(By.NAME, 'user').send_keys(args.username)
    driver.find_element(By.NAME, 'password').send_keys(args.password)
    driver.find_element(By.CLASS_NAME, 'css-14g7ilz-button').click()
    time.sleep(1)

# Get Dashboard and Panels info
def get_dashboard_json(driver, args):
    driver.get(args.host + '/api/search')
    content = driver.page_source
    content = driver.find_element(By.TAG_NAME, 'pre').text
    return json.loads(content)

# Parse UID Dashoboards
def get_dashboard_uid(parsed_json, args):
    dashboards = {}
    for dashboard in parsed_json:
        uri = dashboard['uri']
        dashboards[uri[3:]] = dashboard['uid']

    if args.dashboard in dashboards.keys():
        uid = dashboards[args.dashboard]
        return uid
    else:
        logging.error('Dashboard not found')
        exit()

# TODO: get_json в один метод объединить
# Get Panels info
def get_panel_json(driver, uid, args):
    driver.get(args.host + '/api/dashboards/uid/' + uid)
    content = driver.page_source
    content = driver.find_element(By.TAG_NAME, 'pre').text
    return json.loads(content)

# Structure of Panels by Rows
def panels_by_rows(parsed_json):
    charts = []
    dict_row = {}
    row = 'none'

    for panel in parsed_json['dashboard']['panels']:
        if 'panels' not in panel:
            if panel['type'] == 'row':
                row = panel['title']
            else:
                dict_row['RowTitle'] = row
                dict_row['PanelTitle'] = panel['title']
                dict_row['PanelId'] = panel['id']
                charts.append(dict_row)
                dict_row = {}
        else:
            if panel['type'] == 'row':
                row = panel['title']
            else:
                dict_row['RowTitle'] = row
                dict_row['PanelTitle'] = panel['title']
                dict_row['PanelId'] = panel['id']
                charts.append(dict_row)
                dict_row = {}     
    return charts

# Make dir for Storage 
def make_dir(dir_path):
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

# TODO: Сделать общий метод для создании папок
# TODO: заменить двойные ковычки на ординарные
# TODO: поправить время при снимках
# TODO: for для порядкового отображения
# TODO: если PanelTitle больше опредленной длины не добавляем
# TODO: размер экрана настраиваемый
# TODO: сделать общий метод для получения json
# Make dir for Panels and make Screenshots
def make_screen(driver, charts, args, dash_name, uid, millisec_start, millisec_end):
    i = 1
    for chart in charts:
        if len(args.rows) == 0 or chart['RowTitle'] in args.rows:
            if not os.path.isdir(args.storage_dir + '/' + chart['RowTitle']):
                os.makedirs(args.storage_dir + '/' + chart['RowTitle'])
                i = 1
            url = args.host + '/d-solo/' + uid + "/" + dash_name + "?orgId=" + args.org_id + "&from=" + str(millisec_start) + "&to=" + str(millisec_end) + "&panelId=" + str(chart['PanelId'])
            driver.get(url)
            time.sleep(1)
            path_screen = f'{args.storage_dir}/{chart["RowTitle"].strip()}/{str(i)}_{str(chart["PanelId"])}.png'
            driver.save_screenshot(path_screen)
            logging.info(f'The screenshot is saved. Screen path = {path_screen}, URL = {url}, Panel = "{chart["PanelTitle"]}"')
            i += 1
        else:
            logging.error(f'Rows not found. {charts}')
            exit()

def main():
    logging.basicConfig(level=logging.INFO)
    args = create_args()

    # Connect driver
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=options, executable_path=args.drv_path)
    driver.set_window_size(1920, 1080)
    logging.info('The driver is connected, the screen resolution is 1920 x 1080')

    login(driver, args)

    dash_json = get_dashboard_json(driver, args)

    uid = get_dashboard_uid(dash_json, args)

    panel_json = get_panel_json(driver, uid, args)

    charts = panels_by_rows(panel_json)
    logging.info('Charts have been collected successfully')
    
    # Convert datetime in ms
    dt_start = datetime.strptime(args.time_range_start, '%d.%m.%Y %H:%M:%S')
    millisec_start = int(dt_start.timestamp() * 1000)
    dt_end = datetime.strptime(args.time_range_end, '%d.%m.%Y %H:%M:%S')
    millisec_end = int(dt_end.timestamp() * 1000)

    make_dir(args.storage_dir)

    make_screen(driver, charts, args, args.dashboard, uid, millisec_start, millisec_end)

if __name__ == "__main__":
    main()
