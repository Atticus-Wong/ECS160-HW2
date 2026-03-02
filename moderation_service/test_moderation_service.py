import pytest
from unittest.mock import patch, MagicMock
from moderation_service import (
    check_moderation,
    get_hashtag_from_service,
    moderate,
    ModerateRequest,
)


class TestCheckModeration:
    def test_clean_post_passes(self):
        assert check_moderation("What a beautiful sunny day!") == False

    def test_banned_word_illegal(self):
        assert check_moderation("This is illegal content") == True

    def test_banned_word_fraud(self):
        assert check_moderation("This is a fraud") == True

    def test_banned_word_scam(self):
        assert check_moderation("This is a scam") == True

    def test_banned_word_exploit(self):
        assert check_moderation("This is an exploit") == True

    def test_banned_word_dox(self):
        assert check_moderation("I will dox you") == True

    def test_banned_word_swatting(self):
        assert check_moderation("swatting is bad") == True

    def test_banned_word_hack(self):
        assert check_moderation("I will hack you") == True

    def test_banned_word_crypto(self):
        assert check_moderation("buy crypto now") == True

    def test_banned_word_bots(self):
        assert check_moderation("these are bots") == True

    def test_case_insensitive_uppercase(self):
        assert check_moderation("HACK the planet") == True

    def test_case_insensitive_mixed(self):
        assert check_moderation("CrYpTo currency") == True


class TestGetHashtagFromService:
    @patch("moderation_service.grpc.insecure_channel")
    @patch("moderation_service.hashtagging_pb2_grpc.HashtagServiceStub")
    def test_grpc_called_correctly(self, mock_stub_class, mock_channel):
        mock_stub = MagicMock()
        mock_stub_class.return_value = mock_stub
        mock_response = MagicMock()
        mock_response.hashtag = "#vacation"
        mock_stub.GetHashtag.return_value = mock_response

        result = get_hashtag_from_service("I love the beach")

        assert result == "#vacation"
        mock_stub.GetHashtag.assert_called_once()

    @patch("moderation_service.grpc.insecure_channel")
    @patch("moderation_service.hashtagging_pb2_grpc.HashtagServiceStub")
    def test_grpc_returns_different_hashtags(self, mock_stub_class, mock_channel):
        mock_stub = MagicMock()
        mock_stub_class.return_value = mock_stub
        mock_response = MagicMock()
        mock_response.hashtag = "#travel"
        mock_stub.GetHashtag.return_value = mock_response

        result = get_hashtag_from_service("Traveling the world")

        assert result == "#travel"


class TestModerateEndpoint:
    @patch("moderation_service.get_hashtag_from_service")
    def test_clean_post_returns_hashtag(self, mock_get_hashtag):
        mock_get_hashtag.return_value = "#happy"
        request = ModerateRequest(post_content="Having a great day!")

        result = moderate(request)

        assert result["result"] == "#happy"
        mock_get_hashtag.assert_called_once_with("Having a great day!")

    @patch("moderation_service.get_hashtag_from_service")
    def test_banned_post_returns_failed(self, mock_get_hashtag):
        request = ModerateRequest(post_content="This crypto deal is great")

        result = moderate(request)

        assert result["result"] == "FAILED"
        mock_get_hashtag.assert_not_called()

    @patch("moderation_service.get_hashtag_from_service")
    def test_grpc_not_called_for_banned_posts(self, mock_get_hashtag):
        request = ModerateRequest(post_content="hack the system")

        moderate(request)

        mock_get_hashtag.assert_not_called()

    @patch("moderation_service.get_hashtag_from_service")
    def test_grpc_called_for_clean_posts(self, mock_get_hashtag):
        mock_get_hashtag.return_value = "#sunset"
        request = ModerateRequest(post_content="Beautiful sunset today")

        moderate(request)

        mock_get_hashtag.assert_called_once_with("Beautiful sunset today")
