from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from stocks.models import Stock

User = get_user_model()

class WatchlistAPITests(APITestCase):
    def setUp(self):
        # 1) create a test user & some stocks
        self.user = User.objects.create_user('alice','a@a.com','pass1234')
        self.stock1 = Stock.objects.create(symbol='AAPL', name='Apple')
        self.stock2 = Stock.objects.create(symbol='MSFT', name='Microsoft')
        self.login_url = '/api/auth/login/'
        self.watchlist_url = '/api/watchlists/'

        # 2) log in and store token
        resp = self.client.post(
            self.login_url,
            {'username':'alice','password':'pass1234'},
            format='json'
        )
        token = resp.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_create_and_list_watchlist(self):
        # create a watchlist with two stocks
        create_resp = self.client.post(
            self.watchlist_url,
            {'name':'Tech','stocks':['AAPL','MSFT']},
            format='json'
        )
        self.assertEqual(create_resp.status_code, 201)
        # unwrap the 'data' wrapper to get the new ID
        wid = create_resp.data['data']['id']

        # list all watchlists and verify ours is present
        list_resp = self.client.get(self.watchlist_url, format='json')
        self.assertEqual(list_resp.status_code, 200)
        watchlists = list_resp.data['data']
        self.assertTrue(any(w['id'] == wid for w in watchlists))

    def test_add_and_remove_stock(self):
        # create an empty watchlist
        resp = self.client.post(
            self.watchlist_url,
            {'name':'Empty'},
            format='json'
        )
        wid = resp.data['data']['id']

        # add AAPL to it
        add_resp = self.client.post(
            f'{self.watchlist_url}{wid}/stocks/',
            {'symbol':'AAPL'},
            format='json'
        )
        self.assertEqual(add_resp.status_code, 201)

        # now remove AAPL
        del_resp = self.client.delete(
            f'{self.watchlist_url}{wid}/stocks/AAPL/'
        )
        self.assertEqual(del_resp.status_code, 200)
