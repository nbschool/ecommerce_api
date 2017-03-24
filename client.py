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
                'item_name': 'bla',
                'quantity': 231,
                'subtotal': 123.2
            }
        ], 
        'total_price': 32132
    }
    import pdb; pdb.set_trace()
    resp = requests.post('http://localhost:5000/orders/', json={'order': order})
    #main()
