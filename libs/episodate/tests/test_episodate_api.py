import pytest
import episodate


@pytest.mark.parametrize("tv_show_name", ["arrow", "Bachelor", "Grey's Anatomy"])
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


@pytest.mark.parametrize("tv_show_name", ["arr()w", "B@chel0r", "Grey's An@tomy", "", None])
def test_search_reports_value_error_for_invalid_name(mocker, tv_show_name):
    # Arrange
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"tv_shows": {}}
    mocker.patch("requests.get", return_value=mock_response)
    api_controller = episodate.EpisodateAPI()

    # Act/Assert
    with pytest.raises(ValueError):
        api_controller.search(tv_show_name)


@pytest.mark.parametrize("tv_show_page", [{}, "1", "one"])
def test_search_reports_type_error_for_invalid_page(mocker, tv_show_page):
    # Arrange
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"tv_shows": {}}
    mocker.patch("requests.get", return_value=mock_response)
    api_controller = episodate.EpisodateAPI()
    tv_show_name = "arrow"

    # Act/Assert
    with pytest.raises(TypeError):
        api_controller.search(tv_show_name, page=tv_show_page)


@pytest.mark.parametrize("tv_show_page", [0, -1])
def test_search_reports_value_error_for_invalid_page(mocker, tv_show_page):
    # Arrange
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"tv_shows": {}}
    mocker.patch("requests.get", return_value=mock_response)
    api_controller = episodate.EpisodateAPI()
    tv_show_name = "arrow"

    # Act/Assert
    with pytest.raises(ValueError):
        api_controller.search(tv_show_name, page=tv_show_page)