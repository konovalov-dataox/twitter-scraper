# urls
QUERY_IDS_URL = 'https://abs.twimg.com/responsive-web/client-web/main.d4f5c725.js'

# containers
SEARCH_URL_CONTAINER = 'https://twitter.com/i/api/2/search/adaptive.json?' \
                       'include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1' \
                       '&include_followed_by=1&include_want_retweets=1&include_mute_edge=1' \
                       '&include_can_dm=1&include_can_media_tag=1&skip_status=1&cards_platform=Web-12' \
                       '&include_cards=1&include_ext_alt_text=true&include_quote_count=true' \
                       '&include_reply_count=1&tweet_mode=extended&include_entities=true' \
                       '&include_user_entities=true&include_ext_media_color=true' \
                       '&include_ext_media_availability=true&send_error_codes=true' \
                       '&simple_quoted_tweet=true&q={} since:{}&count=20' \
                       '&tweet_search_mode=live&query_source=typed_query&pc=1&spelling_corrections=1' \
                       '&ext=mediaStats,highlightedLabel,voiceInfo'
CURSOR_CONTAINER = '&cursor={}'
TWEET_URL_CONTAINER = 'https://twitter.com/i/api/graphql/{}/TweetDetail?' \
                      'variables={{"focalTweetId":"{}","with_rux_injections":false,' \
                      '"includePromotedContent":true,"withCommunity":true,"withTweetQuoteCount":true,' \
                      '"withBirdwatchNotes":false,"withSuperFollowsUserFields":false,"withUserResults":true,' \
                      '"withBirdwatchPivots":false,"withReactionsMetadata":false,"withReactionsPerspective":false,' \
                      '"withSuperFollowsTweetFields":false,"withVoice":true}}'
CHILD_TWEETS_URL_CONTAINER = 'https://twitter.com/i/api/graphql/{}/TweetDetail?variables={{"focalTweetId":"{}",' \
                             '"cursor":"{}","referrer":"tweet","with_rux_injections":false,"includePromotedContent"' \
                             ':true,"withCommunity":true,"withTweetQuoteCount":true,"withBirdwatchNotes":false,' \
                             '"withSuperFollowsUserFields":false,"withUserResults":true,"withBirdwatchPivots":false,' \
                             '"withReactionsMetadata":false,"withReactionsPerspective":false,' \
                             '"withSuperFollowsTweetFields":false,"withVoice":true}}'
TWEET_BROWSER_URL_CONTAINER = 'https://twitter.com/{}/status/{}'
USER_URL_CONTAINER = 'https://twitter.com/i/api/graphql/{}/UserByScreenName?variables=' \
                     '{{"screen_name":"{}","withSafetyModeUserFields":true,"withSuperFollowsUserFields":false}}'
USER_BROWSER_URL_CONTAINER = 'https://twitter.com/{}'

# patterns
TWEET_DETAILS_QUERY_ID_PATTERN = r'queryId:"([a-zA-Z\d-]+)",operationName:"TweetDetail"'
USER_DETAILS_QUERY_ID_PATTERN = r'queryId:"([a-zA-Z\d-]+)",operationName:"UserByScreenName"'
