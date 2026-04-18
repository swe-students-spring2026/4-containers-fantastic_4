import pytest
import mongomock
from unittest.mock import patch, MagicMock
from app import app

def get_test_client(mock_db):
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False 
    with patch('app.users', mock_db.users), \
         patch('app.class_notes', mock_db.class_notes):
        return app.test_client()

def test_registration_and_login():
    """test register, login, and logout"""
    mock_db = mongomock.MongoClient().fantastic4
    client = get_test_client(mock_db)

    # register
    client.post('/register', data={'username': 'testuser', 'password': '123'})
    
    # login
    response = client.post('/login', data={
        'username': 'testuser',
        'password': '123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Logout" in response.data  
    assert b"testuser" in response.data

    # logout
    response = client.get('/logout', follow_redirects=True)
    assert "login" in response.request.path

def test_unauthorized_redirect():
    """check that you have to be logged in to see the index page"""
    mock_db = mongomock.MongoClient().fantastic4
    client = get_test_client(mock_db)

    response = client.get('/', follow_redirects=True)
    
    # should redirect back to login page
    assert "login" in response.request.path
    assert b"Login" in response.data 

@patch('requests.post')
def test_audio_upload_flow(mock_ml_post):
    """tests sending audio file to ml client"""
    mock_db = mongomock.MongoClient().fantastic4
    client = get_test_client(mock_db)

    client.post('/register', data={'username': 'testuser2', 'password': '123'})
    client.post('/login', data={'username': 'testuser2', 'password': '123'})

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"transcript": "this is a test transcript"}
    mock_ml_post.return_value = mock_response

    # mock audio file
    data = {'audio_file': (open(__file__, 'rb'), 'test.wav')}
    response = client.post('/', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    assert response.get_json()['transcript'] == "this is a test transcript"