#importing  Modules/packages
import urllib2
import json
import datetime
import csv
import sys
import re
import collections

#setting the default encoding type to utf-8
reload(sys)
sys.setdefaultencoding('utf-8')

#credentials used to grab data from facebook
app_id = "179382712583708"
app_secret = "17ec5469d159ffee29828474a050c1ba"

access_token = app_id + "|" + app_secret

#Thow an exeption if error found, shows message.
try:
    page_id = str(sys.argv[1])
except Exception, e:
    print quit('\nUsage: python '+str(sys.argv[0])+' [Facebook Page ID]\n')

# Help menu
if page_id == "help" or page_id == "-h":
    print "Write page id from the Facebook page link as an argument" \
          "Usage: python astutev1.0 [FB page ID]|help|-h|--help"
else:
    print "For help use argument help or -h"

# For testing the page working fine
def testFacebookPageData(page_id, access_token):
    # construct the URL string
    base = "https://graph.facebook.com/v2.4"
    node = "/" + page_id
    parameters = "/?access_token=%s" % access_token
    url = base + node + parameters

    # retrieve data
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    data = json.loads(response.read())

    print json.dumps(data, indent=4, sort_keys=True)

# incase of http error 500
def request_until_succeed(url):
    req = urllib2.Request(url)
    success = False
    while success is False:
        try:
            response = urllib2.urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception, e:
            print quit('\nUsage: python ' + str(sys.argv[0]) + ' [Facebook Page ID]\n')
            print "Make sure FB page ID is right"
    return response.read()


# gGetting parameters
def getFacebookPageFeedData(page_id, access_token, num_statuses):
    # construct the URL string
    base = "https://graph.facebook.com"
    node = "/" + page_id + "/feed"
    parameters = "/?fields=message,from,comments{message,from},id,permalink_url,likes.summary(true),shares&limit=%s&access_token=%s" % (
    num_statuses, access_token)  # Defining the contents that i want from facebook to processing of data.
    url = base + node + parameters

    # Data retrieval
    data = json.loads(request_until_succeed(url))
    return data


test_status = getFacebookPageFeedData(page_id, access_token, 1)["data"][0]
print json.dumps(test_status, indent=4, sort_keys=True)


def processFacebookPageFeedStatus(status):
    # As we defined the key as python dictionary, so for top-level items, we can simply call the key.

    #Some items not neccessary exists so to check them for existence.

    status_id = status['id']
    status_message = '' if 'message' not in status.keys() else status['message']
    From_name = '' if 'from' not in status.keys() else status['from']['name']
    From_id = '' if 'from' not in status.keys() else status['from']['id']
    #perlinks = '' if 'permalink_url' not in status.keys() else status['permalink_url']
    perlinks = '' if 'permalink_url' not in status.keys() else status['permalink_url']
    stat_comments = '' if 'comments' not in status.keys() else status['comments']
    comments_message = '' if 'comments' not in status.keys() else status['comments']['data'][0]['message']  #These are nested items that requires to be extracted
    comments_from = '' if 'comments' not in status.keys() else status['comments']['data'][0]['from']['name']#These are nested items that requires to be extracted
    num_likes = 0 if 'likes' not in status.keys() else status['likes']['summary']['total_count']            #These are nested items that requires to be extracted


    # returning a tuples of status_id, status_message, From_name, From_id, perlinks, stat_comments, comments_message, comments_from and num_likes
    return status_id, status_message, From_name, From_id, perlinks, stat_comments, comments_message, comments_from, num_likes

processed_test_status = processFacebookPageFeedStatus(test_status)
print processed_test_status

#scrapping all the processed data into a csv file.
def scrapeFacebookPageFeedStatus(page_id, access_token):
    with open('%s_facebook_statusestest.csv' % page_id, 'wb') as file:      #opening file for writing, if not exist creates one
        w = csv.writer(file)
        w.writerow(["status_id", "status_message", "From_name", "From_id", "links", "stat_comments", "comments_message", "comments_from", "num_likes"])

        num_processed = 0                                                     #to keep a count on how many have processed
        scrape_starttime = datetime.datetime.now()

        print "Scraping %s Facebook Page: %s\n" % (page_id, scrape_starttime)   #printing page id and time when the process started

        statuses = getFacebookPageFeedData(page_id, access_token, 100)

        for status in statuses['data']:
            w.writerow(processFacebookPageFeedStatus(status))

        # output progress occasionally to make sure code is not stalling
            num_processed += 1
            if num_processed % 1000 == 0:
                print "%s Statuses Processed: %s" % (num_processed, datetime.datetime.now())

        print "\nDone!\n%s Statuses Processed in %s" % (num_processed, datetime.datetime.now() - scrape_starttime)


def classifier():

    f1 = open('%s_facebook_statusestest.csv' % page_id, 'r')
    f3 = open('%s_facebook_statusestest.csv' % page_id, 'r')

    with open('list.txt', 'rb') as f:
        f2 = f.readlines()

    c1 = csv.reader(f1)
    c2 = csv.reader(f3)

    ar = []
    br = []
    linksr = []

    # putting values of message of all posts into an array
    for row in c1:
        ar.append(str(row[1]))

    # putting values of links of the all posts into an array
    for row in c2:
        linksr.append(str(row[4]))

    #putting in the words in the word list into an array
    for word in f2:
        br.append(word.strip())

    #print linksr
    count = 0

    #creating empty lists to carry the values of results after comparison later
    result = []
    resultlin = []

    # finding posts that contains words from the word list and pass them into new blanck array which was created earlier.
    for a in ar:
        count = count + 1
        for b in br:
            vr = re.findall(b, a)
            if vr != []:
                lin = linksr[count-1]
                result.append(a)
                resultlin.append(lin)
    f1.close()
    f3.close()

    # Classifing the posts according to the number of words/phrases accurring in the post.
    #low risk posts
    classr = [item for item, count in collections.Counter(result).items() if count == 1]
    classlin = [item for item, count in collections.Counter(resultlin).items() if count == 1]
    #Medium risk posts
    class1 = [item for item, count in collections.Counter(result).items() if count == 2]
    classlin1 = [item for item, count in collections.Counter(resultlin).items() if count == 2]
    #high risk posts
    class2 = [item for item, count in collections.Counter(result).items() if count == 3]
    classlin2 = [item for item, count in collections.Counter(resultlin).items() if count == 3]
    #very high risk posts
    class3 = [item for item, count in collections.Counter(result).items() if count > 3]
    classlin3 = [item for item, count in collections.Counter(resultlin).items() if count > 3]


    #printing all level posts along with the links to the posts is the array is not empty otherwise shows a message.
    print "Posts with protential risks:"
    if classr != []:
        for j in classr:
            index_number = classr.index(j)
            print j
            print "Link to the post:"
            print classlin[index_number]
    else:
        print "**No low risk posts**"

    print "-" * 30

    print "Posts with medium risk:"
    if class1 != []:
        for k in class1:
            index_number = class1.index(k)
            print k
            print "Link to the post:"
            print classlin1[index_number]
    else:
        print "**No Medium risk posts**"

    print "-" * 10

    print "Posts with High risk:"
    if class2 != []:
        for l in class2:
            index_number = class2.index(l)
            print l
            print "Link to the post:"
            print classlin2[index_number]
    else:
        print "**No High risk posts**"

    print "-" * 10

    print "Posts with extremely high risk:"
    if class3 != []:
        for m in class3:
            index_number = class3.index(m)
            print m
            print "Link to the post:"
            print classlin3[index_number]
    else:
        print "**No extremely high risk posts**"
    print "-" * 10


#main class
try:
    def main():
        testFacebookPageData(page_id, access_token)
        scrapeFacebookPageFeedStatus(page_id, access_token)
        classifier()

except Exception, e:
    print quit('\nUsage: python ' + str(sys.argv[0]) + ' [Facebook Page ID]\n')
    print "Make sure FB page ID is right"

if __name__ == '__main__':
    main()

