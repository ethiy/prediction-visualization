import io
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import requests
from PIL import Image
import os
import hashlib


def scroll_to_end(wd, sleep_between_interactions):
    wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(sleep_between_interactions)


def get_image_content(image_url):
    try:
        return requests.get(image_url).content
    except Exception as e:
        print(f"Could not download {image_url}: {e}")


def save_image(folder_path: str, image_url: str):
    image_content = get_image_content(image_url)

    try:
        image = Image.open(io.BytesIO(image_content)).convert("RGB")
        file_path = os.path.join(
            folder_path, hashlib.sha1(image_content).hexdigest()[:10] + ".jpg"
        )
        with open(file_path, "wb") as f:
            image.save(f, "JPEG", quality=85)
        print(f"Saved {image_url} as {file_path}.")
    except Exception as e:
        print(f"Could not save {image_url}: {e}")


def fetch_image_urls(query, max_links_to_fetch, wd, sleep_between_interactions):
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"
    wd.get(search_url.format(q=query))

    image_urls = set()
    image_count = 0
    last_thumbnail_count = 0
    while image_count < max_links_to_fetch:
        scroll_to_end(wd, sleep_between_interactions)

        # get all image thumbnail results
        thumbnails = wd.find_elements(By.CSS_SELECTOR, "img.Q4LuWd")
        thumbnail_number = len(thumbnails)

        print(
            f"Extracting links from thumbnails {last_thumbnail_count} to {thumbnail_number}."
        )

        for image in thumbnails[last_thumbnail_count:thumbnail_number]:
            try:
                image.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls
            actual_images = wd.find_elements(By.CSS_SELECTOR, "img.n3VNCb")
            for actual_image in actual_images:
                if actual_image.get_attribute(
                    "src"
                ) and "http" in actual_image.get_attribute("src"):
                    image_urls.add(actual_image.get_attribute("src"))

            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                print(f"Found: {len(image_urls)} image links, done!")
                break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(30)
            load_more_button = wd.find_element(By.CSS_SELECTOR, ".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        last_thumbnail_count = len(thumbnails)

    return image_urls


def search_and_download(query, target_path, number_images):
    target_folder = os.path.join(target_path, "_".join(query.lower().split(" ")))
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    with webdriver.Chrome(service=ChromeService(ChromeDriverManager().install())) as wd:
        image_urls = fetch_image_urls(query, number_images, wd, 0.5)

    for image_url in image_urls:
        save_image(target_folder, image_url)


search_and_download("Morocco football jersey", "./images", 100)
search_and_download("Croatia football jersey", "./images", 100)
search_and_download("France football jersey", "./images", 100)
search_and_download("Argentina football jersey", "./images", 100)
search_and_download("Netherlands football jersey", "./images", 100)
search_and_download("England football jersey", "./images", 100)
search_and_download("Brazil football jersey", "./images", 100)
search_and_download("Portugal football jersey", "./images", 100)
search_and_download("Spain football jersey", "./images", 100)
search_and_download("Japan football jersey", "./images", 100)
