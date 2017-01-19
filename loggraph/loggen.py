import json
import random
from datetime import datetime


# Just a small testing util
def make_logs():
    for i in range(100000):
        date = datetime(2016, 11, random.randrange(1, 20))
        print(json.dumps({
            'timestamp': date.isoformat(),
            'user_id': random.randrange(1, 40000),
            'order': {
                'price': random.randrange(1, 20),
                'item_count': random.randrange(1, 5),
            }
        }))

if __name__ == '__main__':
    make_logs()
