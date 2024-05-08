import json
import sys
from random import randint, sample
from faker import Faker
from collections import OrderedDict
from faker.providers import BaseProvider
class InterestsProvider(BaseProvider):
    def interests(self, num_interests):
        base_interests = [
            'football', 'basketball', 'tennis', 'swimming', 'cycling', # Sports
            'gardening', 'stamp collecting', 'knitting', 'woodworking', 'painting', # Hobbies
            'rock', 'jazz', 'classical', 'pop', 'hip hop', # Music Genres
            'fiction', 'non-fiction', 'mystery', 'sci-fi', 'fantasy', # Book Genres
            'Europe', 'Asia', 'Africa', 'America', 'Antarctica', # Travel
            'gaming', 'programming', 'electronics', 'robotics', 'AI', # Tech
            'cooking', 'baking', 'grilling', 'vegetarian', 'vegan', # Food
            'photography', 'sculpting', 'calligraphy', 'sewing', 'digital art', # Art
            'hiking', 'camping', 'fishing', 'bird watching', 'rock climbing', # Outdoor Activities
            'ballet', 'theater', 'opera', 'stand-up comedy', 'magic', # Performing Arts
            'language learning', 'history', 'philosophy', 'astronomy', 'robotics', # Learning and Education
            'yoga', 'martial arts', 'pilates', 'bodybuilding', 'archery', # Sports and Fitness
            'wine tasting', 'craft beer brewing', 'chocolate making', 'cheese making', 'mixology', # Gastronomy
            'movie watching', 'podcast listening', 'comic book collecting', 'video gaming', 'blogging', # Entertainment and Media
            'backpacking', 'cultural festivals', 'museum visits', 'ecotourism', 'historical sites', # Travel and Culture
            'drone piloting', '3D printing', 'app development', 'cybersecurity', 'virtual reality', # Technology and Gadgets
            'meditation', 'holistic health', 'aromatherapy', 'herbalism', 'mindfulness', # Health and Wellness
            'dog training', 'horse riding', 'bird keeping', 'aquarium care', 'animal rescue', # Pet Care and Animal Welfare
            'furniture making', 'home automation', 'gardening', 'interior decorating', 'landscaping', # Home Improvement and DIY
            'fashion design', 'makeup artistry', 'hair styling', 'jewelry design', 'skincare', # Fashion and Beauty
            'poetry writing', 'novel reading', 'book club participation', 'creative writing', 'literary analysis', # Books and Literature
            'botany', 'ecology', 'physics', 'chemistry experiments', 'stargazing' # Science and Nature
        ]
        return sample(base_interests, min(num_interests, len(base_interests)))

fake = Faker()
fake.add_provider(InterestsProvider)

def fakeprofiles(x):
    return [[randint(18, 70), fake.random_element(elements=OrderedDict([
        ("M", 0.45),("F", 0.45),("NB", 0.1)])), 
        fake.interests(randint(1, 5))] for _ in range(x)]

num_profiles = int(sys.argv[1]) if len(sys.argv) > 1 else 10 
profiles = fakeprofiles(num_profiles)
print(json.dumps(profiles))
