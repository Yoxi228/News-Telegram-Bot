import vk_api
import tweepy
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from config import (
    VK_ACCESS_TOKEN,
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_BEARER_TOKEN,
    logger
)

# Load environment variables
load_dotenv()

class VKParser:
    def __init__(self):
        """Initialize VK parser with API token."""
        self.vk = vk_api.VkApi(token=VK_ACCESS_TOKEN)
        self.api = self.vk.get_api()

    def get_group_id_by_short_name(self, short_name: str) -> int:
        """Get group ID by its short name."""
        try:
            # Get group info by screen name
            group_info = self.api.groups.getById(group_id=short_name)
            if group_info:
                return group_info[0]['id']
            return None
        except Exception as e:
            logger.error(f"Error getting group ID for {short_name}: {str(e)}")
            return None

    def get_group_info(self, group_id):
        """Get VK group information"""
        try:
            group_info = self.api.groups.getById(group_id=group_id)
            return group_info[0] if group_info else None
        except Exception as e:
            logger.error(f"Error getting VK group info: {e}")
            return None

    def get_posts(self, group_id: str, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent posts from a VK group."""
        try:
            # If group_id is a short name, get the actual ID
            if not group_id.isdigit():
                group_id = self.get_group_id_by_short_name(group_id)
                if not group_id:
                    logger.error(f"Could not find group ID for {group_id}")
                    return []

            # Get posts from the group
            posts = self.api.wall.get(
                owner_id=f"-{group_id}",
                count=count,
                filter="owner"
            )

            # Process and format posts
            formatted_posts = []
            for post in posts['items']:
                # Skip ads and suggested posts
                if post.get('marked_as_ads') or post.get('is_pinned'):
                    continue

                # Get post text
                text = post.get('text', '')

                # Get post attachments (photos, videos, etc.)
                attachments = []
                if 'attachments' in post:
                    for att in post['attachments']:
                        if att['type'] == 'photo':
                            # Get the largest photo
                            photo = att['photo']
                            sizes = photo['sizes']
                            largest_photo = max(sizes, key=lambda x: x['width'] * x['height'])
                            attachments.append({
                                'type': 'photo',
                                'url': largest_photo['url']
                            })
                        elif att['type'] == 'video':
                            attachments.append({
                                'type': 'video',
                                'url': f"https://vk.com/video{att['video']['owner_id']}_{att['video']['id']}"
                            })

                # Format post data
                formatted_post = {
                    'id': post['id'],
                    'text': text,
                    'date': datetime.fromtimestamp(post['date']),
                    'attachments': attachments,
                    'likes': post['likes']['count'],
                    'reposts': post['reposts']['count'],
                    'comments': post['comments']['count'],
                    'link': f"https://vk.com/wall-{group_id}_{post['id']}"
                }
                formatted_posts.append(formatted_post)

            return formatted_posts

        except Exception as e:
            logger.error(f"Error getting posts from VK group {group_id}: {str(e)}")
            return []

    def get_new_posts(self, group_id: str, last_post_id: int) -> List[Dict[str, Any]]:
        """Get only new posts since the last post ID."""
        try:
            posts = self.get_posts(group_id)
            return [post for post in posts if post['id'] > last_post_id]
        except Exception as e:
            logger.error(f"Error getting new posts from VK group {group_id}: {str(e)}")
            return []

class TwitterParser:
    def __init__(self):
        try:
            logger.info("Initializing Twitter API v2 client...")

            # Initialize v2 client with bearer token
            self.client = tweepy.Client(
                bearer_token=TWITTER_BEARER_TOKEN,  # Bearer token for v2 API
                consumer_key=TWITTER_API_KEY,
                consumer_secret=TWITTER_API_SECRET,
                access_token=TWITTER_ACCESS_TOKEN,
                access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
                wait_on_rate_limit=True
            )

            # Test the connection
            logger.info("Testing Twitter API v2 connection...")
            test_user = self.client.get_me()
            if test_user.data:
                logger.info(f"Twitter API v2 client initialized successfully. Connected as: @{test_user.data.username}")
            else:
                logger.error("Failed to verify Twitter API credentials")
                raise Exception("Could not verify Twitter API credentials")
        except tweepy.TweepyException as e:
            logger.error(f"Twitter API error during initialization: {str(e)}")
            if hasattr(e, 'response'):
                logger.error(f"Response status code: {e.response.status_code}")
                logger.error(f"Response text: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error initializing Twitter API: {str(e)}")
            raise

    def get_user_info(self, username):
        """Get Twitter user information"""
        try:
            # Remove @ if present
            username = username.lstrip('@')
            logger.info(f"Fetching Twitter user info for: {username}")

            # Get user by username using v2 API
            logger.debug(f"Making API v2 call to get user info for: {username}")
            user = self.client.get_user(
                username=username,
                user_fields=['id', 'name', 'username', 'created_at']
            )

            if not user.data:
                logger.error(f"User not found: {username}")
                return None

            logger.info(f"Successfully found user: {user.data.name} (@{user.data.username})")
            return user.data
        except tweepy.TweepyException as e:
            logger.error(f"Twitter API error getting user info: {str(e)}")
            if hasattr(e, 'response'):
                logger.error(f"Response status code: {e.response.status_code}")
                logger.error(f"Response text: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting Twitter user info: {str(e)}")
            return None

    def get_tweets(self, username, last_tweet_id=None):
        """Get new tweets from Twitter user"""
        try:
            # Remove @ if present
            username = username.lstrip('@')
            logger.info(f"Fetching tweets for user: {username}")

            # Get user ID first
            user = self.client.get_user(username=username)
            if not user.data:
                logger.error(f"User not found: {username}")
                return []

            # Get user's tweets using v2 API
            tweets = self.client.get_users_tweets(
                user.data.id,
                max_results=10,
                tweet_fields=['created_at', 'text', 'id'],
                exclude=['retweets', 'replies']
            )

            if not tweets.data:
                logger.info(f"No tweets found for user: {username}")
                return []

            new_tweets = []
            for tweet in tweets.data:
                if last_tweet_id and tweet.id <= last_tweet_id:
                    break

                new_tweets.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'date': tweet.created_at,
                    'link': f"https://twitter.com/{username}/status/{tweet.id}"
                })

            logger.info(f"Successfully fetched {len(new_tweets)} tweets")
            return new_tweets
        except tweepy.TweepyException as e:
            logger.error(f"Twitter API error getting tweets: {str(e)}")
            if hasattr(e, 'response'):
                logger.error(f"Response status code: {e.response.status_code}")
                logger.error(f"Response text: {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting tweets: {str(e)}")
            return []
