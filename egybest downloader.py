#!C:\Program Files\Python39\python.exe

import os
import sys
import time
import click
import tempfile
import operator
import requests
import webbrowser
from os.path import expanduser
from bs4 import BeautifulSoup
from user_agent import generate_user_agent
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

__author__ = "Yassine Addi"
__copyright__ = "Copyright (C) 2020 Yassine Addi"
__license__ = "MIT"
__version__ = "2020.5.3"

AVAILABLE_QUALITIES = ["1080", "720", "480", "360", "240"]
URL = "https://coon.egybest.com"


def validate_seasons(ctx, param, value):
    # Spaghetti code to validate the seasons argument.
    if not value:
        return value
    try:
        x = tuple()
        for v in value:
            if ":" in v:
                s, ep_list = v.split(":")
                if not ep_list:
                    ep_list = tuple()
            else:
                s, ep_list = v, tuple()

            if isinstance(ep_list, str) and ("," in ep_list or ep_list.isdigit()):
                ep_list = tuple([int(ep) for ep in ep_list.split(",")])
            elif not ep_list:
                pass
            elif ep_list[0] in [">", "<"]:
                if ">" == ep_list[0]:
                    ep_list = (operator.gt, int(ep_list[1:]))
                elif "<" == ep_list[0]:
                    ep_list = (operator.lt, int(ep_list[1:]))
            else:
                raise click.BadArgumentUsage(
                    "Bad argument, please see examples at https://git.io/Jf3Fi"
                )
            x += ((int(s), ep_list),)
        return x
    except Exception as e:
        raise click.BadArgumentUsage(
            "Bad argument, please see examples at https://git.io/Jf3Fi"
        )
    return value


def init_browser(executable_path):
    chrome_options = webdriver.ChromeOptions()
    chrome_prefs = {}
    chrome_prefs["profile.managed_default_content_settings.images"] = 2
    chrome_prefs["profile.default_content_settings.images"] = 2
    # block all downloads
    chrome_prefs["download.download_restrictions"] = 3
    chrome_prefs["download.default_directory"] = tempfile.gettempdir()
    chrome_options.add_experimental_option("prefs", chrome_prefs)
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--headless")
    # run chromedriver in silent mode
    chrome_options.add_argument("--log-level=OFF")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    browser = webdriver.Chrome(executable_path=executable_path, options=chrome_options)
    return browser


def make_safe_filename(unsafe_filename):
    return "".join(
        [c for c in unsafe_filename if c.isalpha() or c.isdigit() or c == " "]
    ).rstrip()


def close_ads(browser):
    for x in reversed(range(1, len(browser.window_handles))):
        browser.switch_to.window(browser.window_handles[x])
        browser.close()
    browser.switch_to.window(browser.window_handles[0])


@click.command()
@click.option(
    "--quality",
    "-Q",
    default="720",
    show_default=True,
    type=click.Choice(AVAILABLE_QUALITIES),
    help="Quality of output video.",
)
@click.option(
    "--output-file",
    "-o",
    type=click.File(mode="w"),
    help="Save download URIs to FILENAME.",
)
@click.option(
    "--dest",
    "-d",
    default=expanduser("~") + os.sep + "Documents/movieslinks",
    help="Destination path.",
)
@click.option(
    "--executable-path",
    "-x",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help="Path to chromedriver executable.",
)
@click.option("--quiet", default=False, is_flag=True, help="Activate quiet mode.")
@click.argument("search", required=False, nargs=1)
@click.argument("seasons", nargs=-1, callback=validate_seasons)
@click.version_option(__version__, prog_name="egybest-dl")
def main(search, quality, seasons, output_file, dest, executable_path, quiet):
    """
    Downloads any Movie or TV Series from EgyBest.


    \b
    Arguments:
      SEARCH\tName of the Movie or TV Series.
      SEASONS\t[season[:episode[,episode[,...]]]]...
    """

    if not executable_path:
        executable_path = "chromedriver"

    fake_user_agent = generate_user_agent()
    if not quiet:
        click.echo("Initializing Chrome")
    try:
        browser = init_browser(executable_path)
    except Exception as e:
        click.echo(str(e))
        sys.exit()

    if not search:
        search = click.prompt("What are you searching for ")

    # some packages are optional
    installed_packages = {}
    try:
        from pySmartDL import SmartDL

        installed_packages["pySmartDL"] = True
    except ImportError:
        pass

    extracted_links = []

    # Headers for common browsers
    headers = {
        "User-Agent": fake_user_agent,
        "Accept-Language": "en,en-US;q=0,5",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8",
    }
    sess = requests.Session()
    while True:
        if not quiet:
            click.echo("Searching for results...")
        r = sess.get(URL + "/autoComplete.php?q={}".format(search), headers=headers)
        results = r.json()
        if not results.get(search):
            click.echo("No results !")
            search = click.prompt("What are you searching for ")
        else:
            break

    response = 0
    if len(results[search]) > 1:
        click.echo()
        click.echo("Results :\n---------")
        for x, ob in enumerate(results[search]):
            click.echo(
                "({})\t{} , Type : {}".format(
                    x + 1, ob["t"], ob["u"].split("/")[0].title()
                )
            )
        response = (
            int(
                click.prompt(
                    "Enter your choice",
                    type=click.Choice(
                        [str(x) for x in range(1, len(results[search]) + 1)]
                    ),
                )
            )
            - 1
        )
        click.echo("Chosen : {}".format(results[search][response]["t"]))
    else:
        click.echo(
            "{} : {}".format(
                results[search][0]["u"].split("/")[0].title(), results[search][0]["t"]
            )
        )

    # To fix a redirect bug, we're obliged to invoke an popup ad for a couple of secs.
    # To emulate this, we'll click on the search field as if we were looking for
    # something, wait 3 secs and close the ad.
    if not quiet:
        click.echo("opening a popup ad for 3 secs...")
    browser.get(URL + "/some404page")  # load it faster...
    try:
        elem = browser.find_element_by_xpath(
            '//input[contains(@class, "autoComplete")]'
        )
        elem.click()
        time.sleep(3)
        close_ads(browser)
    except:
        # If it fails, well, fingers crossed.
        if not quiet:
            click.echo("failed opening popup ad.")

    chosen_result = results[search][response]
    page_links = []

    if not quiet:
        click.echo("Requesting pages links...")
    if chosen_result["u"].lower().startswith("movie"):
        page_links.append(URL + "/{}/".format(chosen_result["u"]))

    else:
        if not seasons:
            try:
                seasons = validate_seasons(
                    None,
                    None,
                    tuple(
                        click.prompt(
                            "What seasons and episodes ? ", prompt_suffix=""
                        ).split()
                    ),
                )
            except Exception as e:
                click.echo(str(e))
                sys.exit()

        l = []
        r = sess.get(URL + "/{}/".format(chosen_result["u"]), headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        nb = len(soup.select('a[href*="/season/"]'))
        if not quiet:
            click.echo("There are {} seasons".format(nb))
        for s, _ in seasons:
            elem = soup.select_one('a[href*="-season-{}/"]'.format(s))
            if elem is not None:
                l.append(elem.attrs["href"])
                if not quiet:
                    click.echo("Season {} added".format(s))
            else:
                if not quiet:
                    click.echo("season {} don't exist !".format(s))

        for x, url in enumerate(l):
            browser.get(url)
            soup = BeautifulSoup(browser.page_source, "html.parser")
            s = seasons[x][0]
            ep_list = seasons[x][1]
            nb = len(soup.select('a[href*="-season-{}-ep-"]'.format(s)))
            if not quiet:
                click.echo("There are {} episodes in season {}".format(nb, s))

            # is it a filtered search?
            if len(ep_list) > 0 and callable(ep_list[0]):
                # build a new list...
                new_ep_list = tuple()
                for ep in range(1, nb + 1):
                    # if the episode matches the condition
                    if ep_list[0](ep, ep_list[1]):
                        # add it to the new list
                        new_ep_list += (ep,)
                # 'None' to distinguish it from downloading all episodes.
                ep_list = new_ep_list if len(new_ep_list) > 0 else None

            if ep_list is None:
                pass
            elif not ep_list:
                elems = soup.select('a[href*="-season-{}-ep-"]'.format(s))
                page_links += [elem.attrs["href"] for elem in elems]
                if not quiet:
                    click.echo("all {} episodes added".format(nb))
            else:
                for ep in ep_list:
                    elem = soup.select_one('a[href*="-season-{}-ep-{}/"]'.format(s, ep))
                    if elem is not None:
                        page_links.append(elem.attrs["href"])
                        if not quiet:
                            click.echo("season {} episode {} added".format(s, ep))
                    else:
                        if not quiet:
                            click.echo("episode {} don't exist !".format(ep))

    old_len = len(page_links)
    page_links = list(set(page_links))
    if old_len != len(page_links):
        if not quiet:
            click.echo("removed duplicate links")
    # sort episodes
    page_links.sort(key=lambda v: int("".join([c for c in v if c.isdigit()])))
    if not quiet:
        click.echo("Gathering download links...")
    cur = 0
    while cur < len(page_links):
        page_link = page_links[cur]
        try:
            if not quiet:
                click.echo("Accessing egybest page --> {}".format(page_link))
            browser.get(page_link)
            if not quiet:
                click.echo("Accessing download page")

            if chosen_result["u"].lower().startswith("movie"):

                movietime = browser.find_elements_by_xpath(
                    '//table[contains(@class, "movieTable")]//tbody//tr[6]//td[2]'
                )

                click.echo(f"movie time is {movietime[0].text}")

                qualities_list = []
                for x in AVAILABLE_QUALITIES:
                    if browser.find_elements_by_xpath(
                        '//table[contains(@class, "dls_table")]//tbody//tr[td//text()[contains(., "{}p")]]//a[1]'.format(
                            x
                        )
                    ):
                        qualities_list.append(x)
                        size = browser.find_elements_by_xpath(
                            '//table[contains(@class, "dls_table")]//tbody//tr//td[contains(., "{}p")]//following::td'.format(
                                x
                            )
                        )
                        click.echo(f"size of {x}p quality is {size[0].text}")
                quality = click.prompt("Choose", type=click.Choice(qualities_list))

            print(quality)
            elem = browser.find_element_by_xpath(
                '//table[contains(@class, "dls_table")]//tr[td//text()[contains(., "{}p")]]//a[1]'.format(
                    quality
                )
            )

            browser.get(URL + elem.get_attribute("data-url"))
        except TimeoutException:
            time.sleep(5)
            continue

        try:
            WebDriverWait(browser, 30).until(lambda x: "VidStream" in browser.title)
        except:
            if not quiet:
                click.echo("failed to access download page, retrying...")
            time.sleep(2)
            continue

        try:
            browser.find_element_by_xpath('//*[contains(text(), "Download")]').click()
            if not quiet:
                click.echo("Ad delay (3 secs)")
            time.sleep(3)
        except NoSuchElementException:
            if not quiet:
                click.echo("failed to locate the download button, retrying...")
            time.sleep(2)
            continue

        if not quiet:
            click.echo("Closing ads")
        close_ads(browser)

        try:
            elem = WebDriverWait(browser, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[contains(text(), "Download")][@href]')
                )
            )
        except TimeoutException:
            time.sleep(2)
            continue

        extracted_links.append(elem.get_attribute("href"))
        if extracted_links[-1] is None:
            del extracted_links[-1]
            click.echo("link is missing , try again? [y/N]", nl=False)
            c = click.getchar()
            click.echo()
            if c.lower() == "y":
                continue
        else:
            click.echo("{} --> added".format(extracted_links[-1].split("/")[-1]))

        cur += 1

    if not quiet:
        click.echo("Quit browser")
    browser.quit()

    if not quiet:
        click.echo("extracted {} links !".format(len(extracted_links)))

    if extracted_links and output_file:
        with output_file.open() as out:
            out.write("\n".join(extracted_links))
        click.echo("saved links to --> {}".format(output_file.name))
    elif extracted_links:
        click.echo("save links ? [y/N]", nl=False)
        c = click.getchar()
        click.echo()
        if c.lower() == "y":
            save_to = (
                dest
                + (os.sep if dest[-1] != os.sep else "")
                + (chosen_result["u"].split("/")[0])
                + " "
                + make_safe_filename(chosen_result["t"])
                + ".txt"
            )
            with open(save_to, "w") as f:
                f.write("\n".join(extracted_links))
                click.echo("saved links to --> {}".format(save_to))

    if extracted_links:
        msg = ["[o]pen URLs in default browser"]
        if installed_packages.get("pySmartDL"):
            msg.append("start [d]ownloading")

        click.echo(", ".join(msg) + " or [Q]uit ?", nl=False)
        c = click.getchar().lower()
        click.echo()
        if c == "o":
            for link in extracted_links:
                webbrowser.open(link)
        elif c == "d" and installed_packages.get("pySmartDL"):
            try:
                for link in extracted_links:
                    ob = SmartDL(link, dest, timeout=30)
                    ob.start()
                    click.echo("downloaded at --> {}".format(ob.get_dest()))
            except Exception as e:
                save_to = (
                    dest
                    + (os.sep if dest[-1] != os.sep else "")
                    + (chosen_result["u"].split("/")[0] + " ")
                    + make_safe_filename(chosen_result["t"])
                    + ".txt"
                )
                click.echo("there were some errors")
                with open(save_to, "w") as f:
                    f.write("\n".join(extracted_links))
                click.echo("download links saved '{}'.".format(save_to))
                sys.exit()


if __name__ == "__main__":
    try:
        main(prog_name="egybest-dl")
    except Exception as e:
        click.echo("error: ")
        time.sleep(3)
        raise
