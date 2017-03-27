from http.client import CREATED
from http.client import NO_CONTENT
from http.client import OK
from urllib.parse import urljoin
import requests
import json

if __name__ == '__main__':
    
    order = {
        'items': [
            {
                'name': 'bla',
                'picture': uuid.uuid4(),
                'price' = 100.00,
                'description' = "item3description."
            }
        ], 
        'total_price': 32132
    }

    #resp = requests.post('http://gitlocalhost:5000/orders/', json={'order':  json.dumps(order)})
    resp = requests.post('http://localhost:5000/orders/', json={'order':  order})
    