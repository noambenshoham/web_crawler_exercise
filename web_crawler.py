from pathlib import Path
import sys
from bs4 import BeautifulSoup
import requests
import json
import validators
from urllib.parse import urlparse

result_file_path = "results.json"

def main():
    main_url = sys.argv[1]
    depth_string = sys.argv[2]
    results = get_results(main_url, 0, int(depth_string))
    
    results_json = {"results": results}
    result_file_path = Path("results.json")
    results_json_string = json.dumps(results_json)
    result_file_path.write_text(results_json_string)

def get_results(url, depth, max_depth):
    results = []
    try:
        html_string = get_web_page(url)
        images_srcs = get_image_srcs(html_string, url)
    except:
        return []
    for image_src in images_srcs:
        results.append({
            "imageUrl": image_src,
            "sourceUrl": url,
            "depth": depth,
        })
    if depth == max_depth:
        return results
    links = get_a_hrefs(html_string)
    for link in links:
        results += get_results(link, depth + 1, max_depth)
    return results

def get_web_page(page_link):
    response = requests.get(page_link)
    file_content = response.text
    return file_content

def get_bg_images(html_string, url):
    bg_images = []
    soup = BeautifulSoup(html_string, "html.parser")
    for items in soup.select("[style*='background-image']"):
        style_attrs = items.get('style').split(";")
        for style_attr in style_attrs:
            if style_attr.startswith('background'):
                bg_images.append(url +'/' + style_attr[22:-2])
    return bg_images

def get_image_srcs(html_string, url):

    html_soup = BeautifulSoup(html_string, "html.parser")
    image_srcs = []
    for image_tag in html_soup.find_all("img"):
        image_src = image_tag["src"]

        if image_src.startswith('data:image/gif;base64') or image_src.startswith('data:image/png;base64'):
            continue
        image_src = refactor_images_url(image_src, url)
        if image_src not in image_srcs:
            image_srcs.append(image_src)
    for bg_image_src in get_bg_images(html_string, url):
        bg_image_src = refactor_images_url(bg_image_src, url)
        image_srcs.append(bg_image_src)

    
    
    return image_srcs

def refactor_images_url(image_src, site_url):
    url_protocol= (urlparse(site_url)).scheme
    url_domain  = urlparse(site_url).netloc
    if image_src.startswith('//'):
        image_src = url_protocol + ":" + image_src
    elif image_src.startswith('/'):
        image_src = url_domain + image_src
    return image_src

def get_a_hrefs(html_string):
    html_soup = BeautifulSoup(html_string, "html.parser")
    a_hrefs = []
    for a_tag in html_soup.find_all("a"):
        if (a_tag.has_key('href')):
            if validators.url(a_tag['href']) == True:
                a_href = a_tag["href"]
                a_hrefs.append(a_href)

    return a_hrefs

if __name__ == "__main__":
    main()
