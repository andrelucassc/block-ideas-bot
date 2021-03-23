from wit import Wit
from requests import get

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('WIT_TOKEN')

def handle_message(response):
    greetings = first_trait_value(response['traits'], 'wit$greetings')
    celebrity = first_entity_resolved_value(response['entities'], 'wit$notable_person:notable_person')
    if celebrity:
        # We can call the wikidata API using the wikidata ID for more info
        return wikidata_description(celebrity)
    elif greetings:
        return 'Hi! You can say something like "Tell me about Beyonce"'
    else:
        return "Um. I don't recognize that name. " \
                "Which celebrity do you want to learn about?"


def wikidata_description(celebrity):
    try:
        wikidata_id = celebrity['external']['wikidata']
    except KeyError:
        return 'I recognize %s' % celebrity['name']
    rsp = get('https://www.wikidata.org/w/api.php', {
        'ids': wikidata_id,
        'action': 'wbgetentities',
        'props': 'descriptions',
        'format': 'json',
        'languages': 'en'
    }).json()
    description = rsp['entities'][wikidata_id]['descriptions']['en']['value']
    return 'ooo yes I know %s -- %s' % (celebrity['name'], description)