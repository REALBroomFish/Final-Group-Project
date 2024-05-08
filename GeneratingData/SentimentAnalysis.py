import sys
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account
# initialising variables, including validation for google cloud translate
analyzer = SentimentIntensityAnalyzer()
credentials = service_account.Credentials.from_service_account_file("location_of_authentication_file.json")
client = translate.Client(credentials=credentials)

def translate_and_analyse_posts(posts):
    translated = client.translate(posts, target_language='en')
    translated_texts = [t['translatedText'] for t in translated]
    sentiments = [analyzer.polarity_scores(text) for text in translated_texts]
    return sentiments


# main process
try:
    # loading variables from the stdin
    input_data = json.loads(sys.stdin.read())
    if not isinstance(input_data, dict) or "posts" not in input_data:
        raise ValueError("Invalid input format. Expected JSON with 'posts'")
    posts = input_data["posts"]
    total_count = input_data["total_count"]
    # returns everything
    print(json.dumps(translate_and_analyse_posts(posts, total_count)))
except:
    sys.exit(1)

