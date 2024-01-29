from atlassian import Confluence
from dateutil.relativedelta import relativedelta
from datetime import datetime

personal_access_token_prod = "prod server token goes here"
production_server = "https://prod server url goes here"
confluence = Confluence(url = production_server, token = personal_access_token_prod, timeout = 1800)
space_counter = 0
current_day = datetime.strftime(datetime.today(), '%Y_%m_%d')
logger = open(current_day +'_page_version_purge_result.txt', 'w', encoding='UTF-8')
three_months = datetime.strptime(datetime.strftime(datetime.today() + relativedelta(months = -3), '%Y-%m-%d'), '%Y-%m-%d')
logger.writelines("Start Time: " + str(datetime.now()) + "\n")
mod = 0
while True:
    for space in confluence.get_all_spaces(start=space_counter, limit=500, expand=None)["results"]:
        mod = mod + 1
        print("Checking space: " + space["key"])
        page_counter = 0
        while True:
            if len(confluence.get_all_pages_from_space(space["key"], start=page_counter, limit=1, status=None, expand=None, content_type='page')) == 1:
                for page in confluence.get_all_pages_from_space(space["key"], start=page_counter, limit=100, status=None, expand=None, content_type='page'):
                    print("Checking page: " + page["title"])
                    if confluence.history(page["id"])["lastUpdated"]["number"] > 1:
                        print("Attempting to remove page history", end = "", flush = True)
                        while True:
                            try:
                                version_one = confluence.get_content_history_by_version_number(page["id"], 1)["when"]
                            except:
                                print("\nPossible issue in versioning. Space: {} | Page: {}".format(space["key"],page["title"]))
                                logger.write("Possible issue in versioning. Space: {} | Page: {}\n".format(space["key"],page["title"]))
                                break

                            version_date = datetime.strptime(str(version_one).split("T")[0], '%Y-%m-%d')
                            if version_date <= three_months:
                                if confluence.history(page["id"])["lastUpdated"]["number"] > 1:
                                    confluence.remove_content_history(page["id"], 1)
                                    print(".", end = "", flush = True)
                                else:
                                    print("Done!")
                                    break
                            else:
                                print("\nIt's not been more than 3 months since the current remaining versions have been edited.")
                                break
                    page_counter = page_counter + 1
                if not page_counter % 100 == 0:
                    break 
            else:
                break
    if not mod % 500 == 0:
        break
    else:
        space_counter = space_counter + 500
logger.writelines("End Time: " + str(datetime.now()) + "\n")
exit()