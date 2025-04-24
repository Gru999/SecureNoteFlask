def test_shared_no_id_redirects(client):
    resp = client.get('/shared_note', follow_redirects=True)
    assert b'No note ID provided' in resp.data


def test_shared_not_found(client, monkeypatch):
    monkeypatch.setattr('app.get_db_connection', lambda: DummyConn([]))
    resp = client.get('/shared_note?note_id=1', follow_redirects=True)
    assert b'Note not found' in resp.data


def test_shared_success(client, monkeypatch):
    note = {'id':7, 'content':'Shared'}
    monkeypatch.setattr('app.get_db_connection', lambda: DummyConn([note]))
    resp = client.get('/shared_note?note_id=7', follow_redirects=False)
    assert resp.status_code == 200
    assert b'Shared' in resp.data


def test_shared_db_exception(client, monkeypatch):
    class ExConn(DummyConn):
        def cursor(self, dictionary=False): raise Exception('fail')
    monkeypatch.setattr('app.get_db_connection', lambda: ExConn())
    resp = client.get('/shared_note?note_id=1', follow_redirects=True)
    assert b'Error:' in resp.data