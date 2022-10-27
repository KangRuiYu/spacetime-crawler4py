import re
import hashlib
import tokenizer
from collections import defaultdict
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from custom_logger import get_logger


'''
- Duplicate content (Kang) (DONE)
- Avoid large files
- Infinate traps (Avery)
- Avoid sites with no info (Vincent)
- Implement tokenizer/parse words (Kang) (DONE)
- Count unique pages (DONE)
- Find longest page in terms of words (Kang) (DONE)
- Find 50 most common words (Kang) (DONE)
- Count subdomains in ics.uci.edu (DONE)
- Filter out stop words for 50 most common words (Avery)(DONE)

sites to ignore:

just picture:
https://duttgroup.ics.uci.edu/2017/12/05/imans-goodbye-lunch/
https://duttgroup.ics.uci.edu/2017/12/20/2017-end-of-the-year-gathering/
https://duttgroup.ics.uci.edu/2017/09/26/2017-fall-quarter-welcoming-bbq/
https://duttgroup.ics.uci.edu/author/maityb/
https://wics.ics.uci.edu/4 --> https://wics.ics.uci.edu/*


error 404:
https://www.ics.uci.edu/404.php
https://luci.ics.uci.edu/LUCIinterace.html#bioFaculty&djp3
https://studentcouncil.ics.uci.edu/clubs.html
http://calendar.ics.uci.edu/calendar.php
https://www.today.uci.edu/department/information_computer_sciences
https://iasl.ics.uci.edu/people/damiri
https://ftp.ics.uci.edu/pub/ietf/http
http://www.ics.uci.edu/pub/ietf/http/rfc1945.html
http://www.ics.uci.edu/pub/ietf/webdav
https://www.ics.uci.edu/~jossher
http://evoke.ics.uci.edu/?page_id=229
http://psearch.ics.uci.edu/about.html


logins:
https://duttgroup.ics.uci.edu/wp-login.php?redirect_to=https%3A%2F%2Fduttgroup.ics.uci.edu%2F2017%2F12%2F20%2F2017-end-of-the-year-gathering%2F {done}
https://intranet.ics.uci.edu {done}

https://duttgroup.ics.uci.edu/wp-login.php?redirect_to=https%3A%2F%2Fduttgroup.ics.uci.edu%2F2017%2F12%2F05%2Fimans-goodbye-lunch%2F
https://duttgroup.ics.uci.edu/wp-login.php?redirect_to=https%3A%2F%2Fduttgroup.ics.uci.edu%2F2017%2F12%2F20%2F2017-end-of-the-year-gathering%2F


traps:
https://wics.ics.uci.edu/events/
    - Contains calendar that goes to prev day that contains empty content.
https://www.informatics.uci.edu/files/pdf/InformaticsBrochure-March2018
    - PDF, very large


blacklist:
https://intranet.ics.uci.edu {done}
https://tippersweb.ics.uci.edu {done}


not interesting:
https://www.stat.uci.edu/ucis-graduate-programs-shine-in-u-s-news-world-report-rankings/
https://tippersweb.ics.uci.edu/covid19/d/oKgkWMDGk/cs-dashboard-mobile?refresh=30s&orgId=1
any url with a share=facebook or share=twitter

for the site:
    https://cml.ics.uci.edu/[something]
    check the class="entry-content" to see if there is any content other than the header

calendar:
https://wics.ics.uci.edu/events/category/wics-meeting-dbh-5011/2022-09 {done}
'''


VALID_DOMAIN_PATTERN = re.compile(".*((\.ics\.uci\.edu\/)|(\.cs\.uci\.edu\/)|(\.informatics\.uci\.edu\/)|(\.stat\.uci\.edu\/)|(today\.uci\.edu\/department\/information_computer_sciences\/)).*")
VALID_DOMAIN_PATTERN2 = re.compile(".*((\.ics\.uci\.edu)|(\.cs\.uci\.edu)|(\.informatics\.uci\.edu)|(\.stat\.uci\.edu)|(today\.uci\.edu\/department\/information_computer_sciences)).*")
ICS_PATTERN = re.compile("ics.uci.edu")
BLACKLIST_PATTERN = re.compile(
    r"login|intranet|tippersweb|wics-meeting-dbh|wics.ics.uci.edu/events/|action=download|" +
    r"share=facebook|share=twitter|pdf"
)

stop_words = set(["a", "about", "above", "after","again", "against", "all", "am", "an", "and", "any",\
    "are", "aren't", "as", "at","be","because","been","before","being","below","between","both","but","by",\
    "can't","cannot","could","couldn't","did","didn't", "do", "does", "doesn't", "doing", "don't", "down" \
    "during", "each", "few", "for","from","further","had","hadn't","has","hasn't","have","haven't",\
    "having","he","he'd","he'll","he's","her","here","here's","hers","herself","him","himself","his", \
    "how","how's","i","i'd","i'll","i'm","i've","if","in","into","is","isn't","it","it's","its","itself", "let's", \
    "me","more", "most","mustn't","my","myself","no","nor","not","of","off","on","once","only","or","other","ought", \
    "our","ours","ourselves","out","over","own","same","shan't","she","she'd","she'll","she's","should","shouldn't","so",\
    "some","such",'than','that',"that's","the","their","theirs","them","themselves","then","there","there's","these",\
    "they","they'd","they'll","they're","they've","this","those","through","to","too","under","until","up","very",\
    "was","wasn't","we","we'd","we'll","we're","we've","were","weren't","what","what's","when","when's","where","where's",\
    "which","while","who","who's","whom","why","why's","with","won't","would","wouldn't","you","you'd","you'll","you're",\
    "you've","your","yours","yourself","yourselves"])

sites_seen = set() # Sites that were added to the frontier.
ics_sites = defaultdict(int) # Sites seen that are ics sites.
site_hashes = set() # Hashes for sites that have been downloaded.

word_freqs = defaultdict(int) # For all downloaded pages.

highest_word_count = -1 # Used to store the longest page.
longest_page_url = ''

blacklist_logger = get_logger("blacklist") # Logger that logs urls that are not valid
duplicate_logger = get_logger("duplicate") # Logger that logs pages with duplicate content.
longest_page_logger = get_logger("longest_page") # Logger that logs when the longest page has been found.
trap_logger = get_logger("trap")
little_words_logger = get_logger("little_words")


def scraper(url, resp):
    links = [link for link in extract_next_links(url, resp) if is_valid(link)]

    for link in links:
        sites_seen.add(link)

        # Check for ics sub domains
        domain = urlparse(link).hostname
        if ICS_PATTERN.search(domain) != None:
            ics_sites[domain] += 1

    return links


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    if (resp.status != 200):
        return []

    site_hash = hashlib.sha256(resp.raw_response.content).hexdigest()

    if (site_hash in site_hashes):
        duplicate_logger.info(f"{url} has duplicate content.")
        return []

    else:
        site_hashes.add(site_hash) # Add content hash to set.

        soup = BeautifulSoup(resp.raw_response.content, "lxml") # Parse html content.

        # Tokenize words in page text, keeping count and updating frequencies.
        word_count = 0

        for word in tokenizer._tokenize_string(soup.get_text()):
            word_count += 1
            if not word in stop_words:
                word_freqs[word] += 1

        # See if page is longer then the current longest page.
        global longest_page_url
        global highest_word_count

        if word_count > highest_word_count:
            longest_page_logger.info(f"{url} is now the longest page with {word_count} words.")
            longest_page_url = url
            highest_word_count = word_count

        # Return links (fragments stripped) for page only if it has more than 100 words.
        if word_count >= 100:
            return [strip_fragment(link.get("href")) for link in soup.find_all("a")]
        else:
            little_words_logger.info(f"{url} only has {word_count} words")
            return []


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        # split_url = url.split("/")
        if parsed.hostname == None:
            return False
        parsed.path.split("/")
        base_url = parsed.scheme + "://" + parsed.hostname + "/".join(parsed.path.split("/")[:6])
        parsed.scheme + "://" + parsed.hostname + "/".join(parsed.path.split("/")[:6])
        #base_url = split_url[0::5].join('/') #something to get the base url
        # if split_url.size >= 7 and base_url in sites_seen:
        #     return False

        # url_robot = url + "/robot.txt"
        # 




        if url in sites_seen:
            return False
        elif parsed.scheme not in set(["http", "https"]):
            return False
        elif VALID_DOMAIN_PATTERN.fullmatch(parsed.hostname) == None and VALID_DOMAIN_PATTERN2.fullmatch(parsed.hostname) == None:
            return False
        elif BLACKLIST_PATTERN.search(url) != None:
            blacklist_logger.info(f"{url} is in the blacklist.")
            return False
        elif base_url in sites_seen and len(parsed.path.split("/")) >= 7:
            trap_logger.info(f"{url} is a trap")
            return False
        

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise


def strip_fragment(url):
    if url != None:
        return url.split("#")[0]
    else:
        return url
