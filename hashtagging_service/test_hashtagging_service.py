import pytest
from unittest.mock import patch, MagicMock
from hashtagging_service import generate_hashtag, HashtagServiceServicer
import hashtagging_pb2


class TestGenerateHashtag:
    @patch("hashtagging_service.client.models.generate_content")
    def test_generate_hashtag_success(self, mock_generate):
        mock_response = MagicMock()
        mock_response.text = "#travel"
        mock_generate.return_value = mock_response

        result = generate_hashtag("I love traveling!")

        assert result == "#travel"
        mock_generate.assert_called_once()

    @patch("hashtagging_service.client.models.generate_content")
    def test_generate_hashtag_different_content(self, mock_generate):
        mock_response = MagicMock()
        mock_response.text = "#food"
        mock_generate.return_value = mock_response

        result = generate_hashtag("Made homemade pasta tonight")

        assert result == "#food"

    @patch("hashtagging_service.client.models.generate_content")
    def test_generate_hashtag_none_response(self, mock_generate):
        mock_response = MagicMock()
        mock_response.text = None
        mock_generate.return_value = mock_response

        result = generate_hashtag("Some post content")

        assert result == "#bskypost"

    @patch("hashtagging_service.client.models.generate_content")
    def test_generate_hashtag_exception(self, mock_generate):
        mock_generate.side_effect = Exception("API Error")

        result = generate_hashtag("Some post content")

        assert result == "#bskypost"

    @patch("hashtagging_service.client.models.generate_content")
    def test_generate_hashtag_strips_whitespace(self, mock_generate):
        mock_response = MagicMock()
        mock_response.text = "  #vacation  "
        mock_generate.return_value = mock_response

        result = generate_hashtag("Beach vacation!")

        assert result == "#vacation"


class TestHashtagServiceServicer:
    @patch("hashtagging_service.generate_hashtag")
    def test_get_hashtag_calls_generate(self, mock_generate):
        mock_generate.return_value = "#happy"
        servicer = HashtagServiceServicer()
        request = MagicMock()
        request.post_content = "Feeling happy today"
        context = MagicMock()

        response = servicer.GetHashtag(request, context)

        assert response.hashtag == "#happy"
        mock_generate.assert_called_once_with("Feeling happy today")

    @patch("hashtagging_service.generate_hashtag")
    def test_get_hashtag_returns_correct_response(self, mock_generate):
        mock_generate.return_value = "#sunset"
        servicer = HashtagServiceServicer()
        request = MagicMock()
        request.post_content = "Beautiful sunset"
        context = MagicMock()

        response = servicer.GetHashtag(request, context)

        assert hasattr(response, "hashtag")
        assert response.hashtag == "#sunset"

    @patch("hashtagging_service.generate_hashtag")
    def test_get_hashtag_handles_fallback(self, mock_generate):
        mock_generate.return_value = "#bskypost"
        servicer = HashtagServiceServicer()
        request = MagicMock()
        request.post_content = "Some content"
        context = MagicMock()

        response = servicer.GetHashtag(request, context)

        assert response.hashtag == "#bskypost"
