from atlassian import Confluence
from dateutil.relativedelta import relativedelta
from datetime import datetime
import time

personal_access_token_prod = "prod server token goes here"
personal_access_token_test = "staging server token goes here"
production_server = "https://prod server url goes here"
test_server = "https://staging server url goes here"
confluence = Confluence(url = production_server, token = personal_access_token_prod, timeout = 1800)

current_day = datetime.strftime(datetime.today(), '%Y_%m_%d')
logger = open(current_day +'_page_version_purge_result.txt', 'w', encoding='UTF-8')
two_years = datetime.strptime(datetime.strftime(datetime.today() + relativedelta(years = -2), '%Y-%m-%d'), '%Y-%m-%d')

def clean_all_page_version_history(space_key):
    page_counter = 0
    while True:
        if len(confluence.get_all_pages_from_space(space_key, start=page_counter, limit=1, status=None, expand=None, content_type='page')) == 1:
            for page in confluence.get_all_pages_from_space(space_key, start=page_counter, limit=100, status=None, expand=None, content_type='page'):
                #time.sleep(0.3)
                print("Checking page: " + page["title"])
                if confluence.history(page["id"])["lastUpdated"]["number"] > 1:
                    print("Attempting to remove page history", end = "", flush = True)
                    while True:
                        try:
                            version_one = confluence.get_content_history_by_version_number(page["id"], 1)["when"]
                        except:
                            print("\nPossible issue in versioning. Space: {} | Page: {}".format(space_key,page["title"]))
                            logger.write("Possible issue in versioning. Space: {} | Page: {}\n".format(space_key,page["title"]))
                            break

                        version_date = datetime.strptime(str(version_one).split("T")[0], '%Y-%m-%d')
                        if version_date <= two_years:
                            if confluence.history(page["id"])["lastUpdated"]["number"] > 1:
                                confluence.remove_content_history(page["id"], 1)
                                print(".", end = "", flush = True)
                            else:
                                print("Done!")
                                break
                        else:
                            print("\nIt hasn't been more than 2 years since the current remaining versions have been edited.")
                            break
                page_counter = page_counter + 1
            if not page_counter % 100 == 0:
                break 
        else:
            break

def clean_all_version_history_from_all_spaces():
    space_counter = 0
    logger.writelines("Start Time: " + str(datetime.now()) + "\n")
    mod = 0
    while True:
        for space in confluence.get_all_spaces(start=space_counter, limit=500, expand=None)["results"]:
            mod = mod + 1
            print("Checking space: " + space["key"])
            clean_all_page_version_history(space["key"])
        if not mod % 500 == 0:
            break
        else:
            space_counter = space_counter + 500
    logger.writelines("\nEnd Time: " + str(datetime.now()))
    return 0

if __name__ == "__main__":
    clean_all_version_history_from_all_spaces()
    exit()