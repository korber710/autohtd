import pytest
import episodate


@pytest.mark.parametrize("tv_show_name", ["arrow", "Bachelor"])
def test_search_with_valid_name(mocker, tv_show_name):
    # Arrange
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"tv_shows": {}}
    mocker.patch("requests.get", return_value=mock_response)

    # Act
    api_controller = episodate.EpisodateAPI()
    tv_shows = api_controller.search(tv_show_name)

    # Assert
    assert tv_shows == {}


@pytest.mark.parametrize("tv_show_id", ["arrow", "29560"])
def test_lookup_with_valid_identifier(mocker, tv_show_id):
    # Arrange
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mocker.patch("requests.get", return_value=mock_response)

    # Act
    api_controller = episodate.EpisodateAPI()
    show_details = api_controller.lookup(tv_show_id)

    # Assert
    assert show_details == {}


@pytest.mark.integration
@pytest.mark.parametrize("tv_show_name", ["arrow", "Bachelor"])
def test_search(tv_show_name):
    # Arrange
    api_controller = episodate.EpisodateAPI()

    # Act
    tv_shows = api_controller.search(tv_show_name)

    # Assert
    assert tv_shows != None
    assert len(tv_shows) > 0


@pytest.mark.integration
@pytest.mark.parametrize("tv_show_id", ["arrow", "29560"])
def test_lookup(tv_show_id):
    # Arrange
    api_controller = episodate.EpisodateAPI()

    # Act
    show_details = api_controller.lookup(tv_show_id)

    # Assert
    assert show_details != None
