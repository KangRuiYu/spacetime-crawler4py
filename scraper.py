import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup


'''
- Duplicate content (Kang)
- Avoid large files
- Infinate traps (Avery)
- Avoid sites with no info (Vincent)
- Implement tokenizer/parse words (Kang)
- Count unique pages
- Find longest page in terms of words
- Find 50 most common words
- Count subdomains in ics.uci.edu

sites to ignore:

just picture:
https://duttgroup.ics.uci.edu/2017/12/05/imans-goodbye-lunch/
https://duttgroup.ics.uci.edu/2017/12/20/2017-end-of-the-year-gathering/
https://duttgroup.ics.uci.edu/2017/09/26/2017-fall-quarter-welcoming-bbq/
https://duttgroup.ics.uci.edu/author/maityb/

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


logins:
https://duttgroup.ics.uci.edu/wp-login.php?redirect_to=https%3A%2F%2Fduttgroup.ics.uci.edu%2F2017%2F12%2F20%2F2017-end-of-the-year-gathering%2F
https://intranet.ics.uci.edu

https://duttgroup.ics.uci.edu/wp-login.php?redirect_to=https%3A%2F%2Fduttgroup.ics.uci.edu%2F2017%2F12%2F05%2Fimans-goodbye-lunch%2F
https://duttgroup.ics.uci.edu/wp-login.php?redirect_to=https%3A%2F%2Fduttgroup.ics.uci.edu%2F2017%2F12%2F20%2F2017-end-of-the-year-gathering%2F


blacklist:
https://intranet.ics.uci.edu
https://tippersweb.ics.uci.edu

not interesting:
https://www.stat.uci.edu/ucis-graduate-programs-shine-in-u-s-news-world-report-rankings/
https://tippersweb.ics.uci.edu/covid19/d/oKgkWMDGk/cs-dashboard-mobile?refresh=30s&orgId=1

for the site:
    https://cml.ics.uci.edu/[something]
    check the cclass="entry-content" to see if there is any content other than the header


'''

sites_seen = set()


def scraper(url, resp):
    links = [link for link in extract_next_links(url, resp) if is_valid(link)]

    for link in links:
        sites_seen.add(link)

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

    soup = BeautifulSoup(resp.raw_response.content, 'lxml')
    links = []

    for link in soup.find_all('a'):
        links.append(link.get('href'))
   
    return links


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)

        valid_domain_pattern = re.compile(".*((\.ics\.uci\.edu\/)|(\.cs\.uci\.edu\/)|(\.informatics\.uci\.edu\/)|(\.stat\.uci\.edu\/)|(today\.uci\.edu\/department\/information_computer_sciences\/)).*")
        valid_domain_pattern2 = re.compile(".*((\.ics\.uci\.edu)|(\.cs\.uci\.edu)|(\.informatics\.uci\.edu)|(\.stat\.uci\.edu)|(today\.uci\.edu\/department\/information_computer_sciences)).*")

        if url in sites_seen:
            return False
        elif parsed.scheme not in set(["http", "https"]):
            return False
        elif valid_domain_pattern.fullmatch(str(parsed.netloc)) == None and valid_domain_pattern2.fullmatch(str(parsed.netloc)) == None:
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
