from unittest.mock import patch, MagicMock
from io import BytesIO
import pytest
import mongomock
from app import app

def get_test_context():
    """helper function for test client"""
    # mock db
    mock_db = mongomock.MongoClient().fantastic4
    
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    # test client
    client = app.test_client()
    
    return client, mock_db.users, mock_db.class_notes

def test_registration_and_login():
    """test register, login, and logout"""
    client, mock_users, _ = get_test_context()

    with patch('app.users', mock_users):
        # register
        client.post('/register', data={'username': 'testuser', 'password': '123'})
        
        assert mock_users.find_one({'username': 'testuser'}) is not None

        # login
        response = client.post('/login', data={
            'username': 'testuser',
            'password': '123'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b"Logout" in response.data
        assert b"testuser" in response.data

def test_unauthorized_redirect():
    """check that you have to be logged in to see the index page"""
    client, _, _ = get_test_context()

    response = client.get('/', follow_redirects=True)

    assert "login" in response.request.path
    assert b"Login" in response.data

@patch('requests.post')
def test_audio_upload_flow(mock_ml_post):
    """tests sending audio file to ml client"""
    client, mock_users, mock_notes = get_test_context()

    with patch('app.users', mock_users), patch('app.class_notes', mock_notes):
        
        client.post('/register', data={'username': 'testuser2', 'password': '123'})
        client.post('/login', data={'username': 'testuser2', 'password': '123'})

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"transcript": "this is a test transcript"}
        mock_ml_post.return_value = mock_response

        # mock audio file
        data = {'audio_file': (BytesIO(b"fake_audio"), 'test.wav')}
        response = client.post('/', data=data, content_type='multipart/form-data')

        assert response.status_code == 200
        assert response.get_json()['transcript'] == "this is a test transcript"
        