import getpass, re
import os, click
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import reusable_module as web


class G_Manga:
    def __init__(self, link):
        self.link = link
        self.driver = web.init_driver("firefox")
        self.driver.get(link)
        self.found_mangas = None
        self.chosen_manga_link = None
        self.chosen_manga_name = None
        self.folder_to_store_manga = None
        self.basic_info = None
        self.manga_folders = None
        self.chosen_folder = None
        self.folder_chapters = None
        self.chosen_chapter_name = None
        self.chosen_chapter_link = None
        self.manga_folders_info = None
        self.chosen_chapter_imsges = None
        self.pdf = None

    def search_mangas(self):
        manga_name = input("Enter name of manga: ")
        search_box = self.driver.find_element(By.ID, "quickSearch")
        search_box.send_keys(manga_name)
        self.driver.implicitly_wait(10)
        self.found_mangas = self.driver.find_elements(
            By.XPATH, "//div[@id='react-autowhatever-quickSearch']/div[1]/ul/li/a"
        )

        if not self.found_mangas:
            print("\nno mangas found, try again\n")
            self.search_mangas()

    def display_mangas(self):
        # suggested mangas according to search
        print("suggested mangas from search:")
        for num, link in enumerate(self.found_mangas, start=1):
            name = link.get_attribute("href").split("/")[-1]
            print(
                f"\n{num}.{name}",
            )

    def choose_manga(self):
        # get the manga from the list
        choices = list(str(n) for n in range(1, len(self.found_mangas) + 1))
        chosen = click.prompt("\nchoose ", type=click.Choice(choices))
        chosen_manga = self.found_mangas[int(chosen) - 1]
        self.chosen_manga_link = chosen_manga.get_attribute("href")
        self.chosen_manga_name = self.chosen_manga_link.split("/")[-1]

    def create_folder_to_store_manga(self):
        # create folder for chosen manga
        path = f"C:\\Users\\{getpass.getuser()}\\Desktop"
        self.folder_to_store_manga = os.path.join(
            path, f"manga\\{self.chosen_manga_name}"
        )
        if not os.path.exists(self.folder_to_store_manga):
            print("\ncreating folder...")
            os.makedirs(self.folder_to_store_manga)
            print("\nfolder created")

    def get_basic_info(self):
        # get some info about the manga
        link = self.driver.current_url
        name = self.driver.find_element(By.XPATH, "//div/div/h1").text
        story = self.driver.find_element(By.CLASS_NAME, "manga-summary").text

        info = {"name": name, "link": link, "story": story}
        return info

    def load_content(self):
        # view all content
        print("\nloading all content...")
        num_of_scrolls = 25
        while num_of_scrolls:
            self.driver.execute_script("window.scrollBy(0,250)")
            sleep(3)
            num_of_scrolls -= 1

    def get_manga_folders(self):
        folders_path = '//div[@id="infiniteVolumes"]/div[2]/div/div/div'
        self.manga_folders = self.driver.find_elements(By.XPATH, folders_path)
        self.manga_folders.reverse()

    def display_folders(self):
        print("\nfolders:")
        for folder in self.manga_folders:
            name = folder.find_element(By.CLASS_NAME, "title").text
            print(f"{name}")

    def choose_folder(self):
        # choose a folder
        print("\nchoose a folder:")
        folders_order = list(str(n) for n in range(1, len(self.manga_folders) + 1))
        chosen = click.prompt("\nchoose ", type=click.Choice(folders_order))
        self.chosen_folder = self.manga_folders[int(chosen) - 1]

    def get_chapters(self):
        # chapters for chosen folder
        self.chosen_folder.click()  # open the folder
        self.driver.execute_script("window.scrollBy(0,570)")
        self.folder_chapters = self.chosen_folder.find_elements(
            By.CLASS_NAME, "chapter-item"
        )
        self.folder_chapters.reverse()

    def display_chapters(self):
        print(f"chapters for this folder:")
        for chapter in self.folder_chapters:
            chapter_name = chapter.find_element(By.XPATH, "div/div[3]/div").text
            print(f"chapter {chapter_name}")

    def choose_chapter(self):
        print("\nchoose a chapter:")
        choices = list(str(n) for n in range(1, len(self.folder_chapters) + 1))
        chosen = click.prompt("\nchoose ", type=click.Choice(choices))
        chosen_chapter = self.folder_chapters[int(chosen) - 1]
        name_path = "div/div[3]/div"
        self.chosen_chapter_name = chosen_chapter.find_element(By.XPATH, name_path).text
        link_path = "div/div[2]/a"
        self.chosen_chapter_link = chosen_chapter.find_element(
            By.XPATH, link_path
        ).get_attribute("href")

    def change_settings(self):
        settings = self.driver.find_element(By.CSS_SELECTOR, ".fa-cog")
        settings.click()
        # to make the image bigger
        self.driver.find_element(By.XPATH, "//div/div[2]/div[2]/button[1]").click()
        # to make the image quality better
        self.driver.find_element(By.XPATH, "//div/div[2]/div[6]/button[2]").click()
        # to apply the changes
        self.driver.find_element(By.XPATH, "//div/div[3]/div/button[2]").click()
        # to hide bars
        self.driver.find_element(By.ID, "WLA").click()

    def get_images(self):
        # link for chosen chapter
        path = '//div[@id="readerContent"]/div/div[2]/img'
        # scroll to the buttom of the page
        sleep(1)
        self.chosen_chapter_imsges = self.driver.find_elements(By.XPATH, path)

    def create_pdf(self):
        # create pdf
        print("\ncreating pdf...")
        name = re.sub(r"[^\w]", "-", self.chosen_chapter_name)
        self.pdf = open(f"{self.folder_to_store_manga}\\{name}.pdf", "wb")
        print("\npdf created")
        print("\npdf saved to:")
        print(f"{self.folder_to_store_manga}")

    def execute(self):
        self.search_mangas()
        self.display_mangas()
        self.choose_manga()
        self.driver.get(self.chosen_manga_link)
        self.create_folder_to_store_manga()
        self.load_content()
        self.get_basic_info()
        self.get_manga_folders()
        self.display_folders()
        self.choose_folder()
        self.get_chapters()
        self.display_chapters()
        self.choose_chapter()
        self.driver.get(self.chosen_chapter_link)
        self.load_content()
        self.change_settings()
        self.get_images()
        self.create_pdf()
        web.save_images_to_pdf(self.chosen_chapter_images, self.pdf)
        self.pdf.close()
        sleep(60)
        self.driver.quit()

    def __call__(self):
        self.execute()


if __name__ == "__main__":
    manga = G_Manga(link="https://gmanga.org/")
    manga()
