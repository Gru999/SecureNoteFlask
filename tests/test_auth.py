def test_get_register(client):
    resp = client.get('/register')
    assert resp.status_code == 200
    assert b'name="username"' in resp.data


def test_post_register_success(client, monkeypatch):
    monkeypatch.setattr('app.get_db_connection', lambda: DummyConn())
    resp = client.post('/register', data={'username':'u','password':'p'}, follow_redirects=True)
    assert b'Registration successful' in resp.data
    assert resp.request.path == '/login'


def test_post_register_failure(client, monkeypatch):
    class ErrConn(DummyConn):
        def cursor(self, dictionary=False):
            raise Exception("duplicate entry")
    monkeypatch.setattr('app.get_db_connection', lambda: ErrConn())
    resp = client.post('/register', data={'username':'u','password':'p'})
    assert b'Error:' in resp.data


def test_login_success(client, monkeypatch):
    # prepare a hashed password
    from werkzeug.security import generate_password_hash
    pw = generate_password_hash('secret')
    user = {'id':1, 'username':'u', 'password':pw}
    monkeypatch.setattr('app.get_db_connection', lambda: DummyConn([user]))
    resp = client.post('/login', data={'username':'u','password':'secret'}, follow_redirects=True)
    assert b'Login successful' in resp.data
    with client.session_transaction() as sess:
        assert sess['user_id'] == 1
        assert sess['username'] == 'u'


def test_login_failure(client, monkeypatch):
    monkeypatch.setattr('app.get_db_connection', lambda: DummyConn([{}]))
    resp = client.post('/login', data={'username':'u','password':'bad'}, follow_redirects=True)
    assert b'Invalid username or password' in resp.data


def test_logout(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    resp = client.get('/logout', follow_redirects=True)
    assert b'You have been logged out' in resp.data
    with client.session_transaction() as sess:
        assert 'user_id' not in sess