from pathlib import Path
import sys
from bs4 import BeautifulSoup
import requests
import json
import validators
# import cssutils

result_file_path = "results.json"

def main():
    main_url = sys.argv[1]
    depth_string = sys.argv[2]
    results = get_results(main_url, int(depth_string))
    print(results)
    results_json = {"results": results}
    result_file_path = Path("results.json")
    results_json_string = json.dumps(results_json)
    result_file_path.write_text(results_json_string)

def get_results(url, maxDepth):
    results = []
    for depth in range(maxDepth + 1):
        html_string = get_web_page(url)
        images_links = get_image_srcs(html_string, url)
        for image in images_links:
            results.append({
                "imageUrl": image,
                "sourceUrl": url,
                "depth": depth,
            })
        
        for url in get_a_hrefs(html_string):
            if (url[:4] == 'http') & (depth < maxDepth):
                depth_results = get_results(url, depth)
                results += depth_results
    print(results)
    return results

def get_web_page(page_link):
    response = requests.get(page_link)
    file_content = response.text
    return file_content

def get_image_srcs(html_string, url):
    html_soup = BeautifulSoup(html_string, "html.parser")
    image_srcs = []
    for image_tag in html_soup.find_all("img"):
        image_src = image_tag["src"]
        if image_src.startswith('data:image/gif;base64'):
            continue
        if image_src.startswith('//'):
            image_src = image_src[2:]
        elif image_src.startswith('/'):
            image_src = image_src[1:]
        image_srcs.append(image_src)
    
    # div_style = html_soup.find('div')['style']
    # style = cssutils.parseStyle(div_style)
    # url = style['background-image']
    # print(url)
    return image_srcs

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
