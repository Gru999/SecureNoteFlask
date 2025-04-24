def test_home_requires_login(client):
    resp = client.get('/', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_home_shows_notes_when_logged_in(client, monkeypatch):
    notes = [{'id':1, 'content':'Note1'}]
    def conn_with_notes(): return DummyConn(notes)
    monkeypatch.setattr('app.get_db_connection', conn_with_notes)
    with client.session_transaction() as sess:
        sess['user_id'] = 42
    resp = client.get('/', follow_redirects=True)
    assert b'Note1' in resp.data


def test_add_note_success(client, monkeypatch):
    monkeypatch.setattr('app.get_db_connection', lambda: DummyConn())
    with client.session_transaction() as sess:
        sess['user_id'] = 99
    resp = client.post('/add', data={'content':'Test'}, follow_redirects=True)
    assert b'Note added successfully' in resp.data


def test_add_note_without_login(client):
    resp = client.post('/add', data={'content':'X'}, follow_redirects=True)
    assert b'You must be logged in to add a note' in resp.data


def test_delete_note(client, monkeypatch):
    monkeypatch.setattr('app.get_db_connection', lambda: DummyConn())
    resp = client.get('/delete/5', follow_redirects=True)
    assert b'Note deleted successfully' in resp.data


def test_view_note_not_found(client):
    resp = client.get('/note', follow_redirects=False)
    assert resp.status_code == 404


def test_view_note_success(client, monkeypatch):
    note = {'id':10, 'content':'Hello'}
    monkeypatch.setattr('app.get_db_connection', lambda: DummyConn([note]))
    resp = client.get('/note?note_id=10', follow_redirects=False)
    assert resp.status_code == 200
    assert b'Hello' in resp.data