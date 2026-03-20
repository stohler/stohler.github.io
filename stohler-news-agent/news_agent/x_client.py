from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass

import requests
import tweepy


@dataclass(slots=True)
class XCredentials:
    api_key: str
    api_secret: str
    access_token: str
    access_token_secret: str


class XPublisher:
    def __init__(self, credentials: XCredentials) -> None:
        self._oauth1 = tweepy.OAuth1UserHandler(
            consumer_key=credentials.api_key,
            consumer_secret=credentials.api_secret,
            access_token=credentials.access_token,
            access_token_secret=credentials.access_token_secret,
        )
        self._v1_api = tweepy.API(self._oauth1)
        self._v2_client = tweepy.Client(
            consumer_key=credentials.api_key,
            consumer_secret=credentials.api_secret,
            access_token=credentials.access_token,
            access_token_secret=credentials.access_token_secret,
        )

    def publish(self, text: str, image_url: str | None = None) -> str:
        media_ids: list[str] | None = None
        if image_url:
            media_id = self._upload_media_from_url(image_url)
            if media_id:
                media_ids = [media_id]

        response = self._v2_client.create_tweet(text=text, media_ids=media_ids)
        data = getattr(response, "data", {}) or {}
        tweet_id = data.get("id", "")
        return str(tweet_id)

    def _upload_media_from_url(self, image_url: str) -> str | None:
        try:
            image_response = requests.get(
                image_url,
                timeout=(8, 20),
                headers={"User-Agent": "stohler-news-agent/0.1"},
            )
            image_response.raise_for_status()
            content_type = image_response.headers.get("content-type", "image/jpeg")
        except requests.RequestException:
            return None

        suffix = ".jpg"
        if "png" in content_type:
            suffix = ".png"
        elif "webp" in content_type:
            suffix = ".webp"

        temp_path = ""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(image_response.content)
                temp_path = temp_file.name
            media = self._v1_api.media_upload(filename=temp_path)
            return str(media.media_id_string)
        except Exception:
            return None
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

