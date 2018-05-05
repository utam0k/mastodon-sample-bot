import random
import bisect
import itertools
import random
import re
import configparser
import os

from mastodon import Mastodon, StreamListener
# import pyowm

def convert_weather_word(weather):
    if weather in weather_phrases.keys():
        return weather_phrases[weather]
    return weather

def is_included(s, l):
    return len([a for a in l if s.find(a) > -1]) > 0

class IzuminStreamListener(StreamListener):

    def on_update(self, status):
        if status['application'] is not None and status['application']['name'] == config['Mastodon']['APP_NAME']:
            return

        content = status['content']
        account = status['account']

        is_me = is_included(content, my_names)
        is_izumin = is_included(content, izumin)

        if is_me:
            if content.find("天気") > -1 :
                mastodon.status_favourite(status['id'])
                regex = r"[\s|,|、|。|.|!|！](.*)[県|府|都|市|区|町|の]"
                matches = re.findall(regex, content)
                if len(matches) < 1:
                    return

                try:
                    observation = owm.weather_at_place('%s' % (matches[0]))
                    w = observation.get_weather()

                    temp = w.get_temperature(unit='celsius')['temp']
                    weather = convert_weather_word(w.get_status())
                    toot_content = '@%s %sの天気は%s、気温は%s度だよ' % (account['username'], matches[0], weather, temp)
                except:
                    toot_content = '@%s ごめんね。%sの天気はわからなかった' % (account['username'], matches[0])

                # Ref: http://mastodonpy.readthedocs.io/en/latest/index.html#mastodon.Mastodon.status_post
                mastodon.status_post(toot_content, in_reply_to_id = status["id"], visibility='private')

        elif is_izumin:
            izumin_status = a[f()]
            # mastodon.toot('%s toot from bot' % (izumin_status), spoiler_text='ここだけの話いずみんは')

def init(config):
    API_BASE_URL = config['Mastodon']['API_BASE_URL']

    if not os.path.exists('clientcred.secret'):
        Mastodon.create_app(
            config['Mastodon']['APP_NAME'],
            api_base_url = API_BASE_URL,
            to_file = 'clientcred.secret'
        )

    mastodon = Mastodon(
        client_id = 'clientcred.secret',
        api_base_url = API_BASE_URL
    )

    mastodon.log_in(
        config['Mastodon']['EMAIL'],
        config['Mastodon']['PASS_WORD'],
        to_file = 'usercred.secret'
    )

    return mastodon

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')

    # owm = pyowm.OWM(config['OWM']['API_KEY']) 

    mastodon = init(config)

    my_names = ['utam0k', "うたもく", "大尊師"]
    izumin = ['izumin', "いずみん"]

    izumin_statuses = [('早漏', 50), ('アイドル', 10), ('癒し担当', 10), ('かわいい', 20), ('🤔', 10)]
    a, w = zip(*izumin_statuses)
    ac = list(itertools.accumulate(w))
    f = lambda : bisect.bisect(ac, random.random() * ac[-1])

    weather_phrases = {'Clear': 'はれ', 'Clouds': 'くもり', 'Rain': 'あめ' ,"snow": 'ゆき'}

    mastodon.stream_local(IzuminStreamListener(), async=False)
    # mastodon.stream_user(IzuminStreamListener(), async=False)
