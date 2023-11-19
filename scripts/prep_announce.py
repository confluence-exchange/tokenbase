from urllib.parse import urlparse
import yaml
import os.path

def get_link(token_info, link_key):
    if "links" not in token_info:
        return None

    for link in token_info["links"]:
        k, v = list(link.items())[0]
        if k == link_key:
            return v
    return None

def print_all_wrap(announcements):
    for ann in announcements:
        print(ann, "\n\n")

def twitter_style(token_info):
    """
    Blah Token $BLAH by [@blah_com|blah.com] is now available on Confluence DEX:

    https://confluence-exchange.github.io/#!/trade/BLAH-ETC

    #{symbol} #ERC20 #gems #EthereumClassic #ICO #Crypto #cryptotrading
    """

    twitter = get_link(token_info, "Twitter")
    if twitter:
        issuer_attr = "@{}".format(urlparse(twitter).path.strip("/"))
    else:
        issuer_attr = get_link(token_info, "Website")

    symbol = token_info["symbol"] if not "__CONFLUENCEDEX_CUSTOM_SYMBOL" in token_info else token_info["__CONFLUENCEDEX_CUSTOM_SYMBOL"]

    token_name = token_info["name"]
    if "token" not in token_name.lower():
        token_name += " Token"

    return "{token_name} ${symbol} by {issuer_attr} is now available on @ConfluenceDEX: https://confluence-exchange.github.io/#!/trade/{symbol}-ETC \n\n#{symbol} #ERC20 #gems #EthereumClassic #ICO #Crypto #cryptotrading".format(
        token_name=token_name, symbol=symbol, issuer_attr=issuer_attr,
    )

def twitter_short_style(token_info):
    """
    Blah Token $BLAH by [@blah_com|blah.com] https://confluence-exchange.github.io/#!/trade/BLAH-ETC
    """

    twitter = get_link(token_info, "Twitter")
    if twitter:
        issuer_attr = "@{}".format(urlparse(twitter).path.strip("/"))
    else:
        issuer_attr = get_link(token_info, "Website")

    symbol = token_info["symbol"] if not "__CONFLUENCEDEX_CUSTOM_SYMBOL" in token_info else token_info["__CONFLUENCEDEX_CUSTOM_SYMBOL"]

    token_name = token_info["name"]
    if "token" not in token_name.lower():
        token_name += " Token"

    return "{token_name} ${symbol} by {issuer_attr} https://confluence-exchange.github.io/#!/trade/{symbol}-ETC #{symbol}".format(
        token_name=token_name, symbol=symbol, issuer_attr=issuer_attr,
    )

def twitter_short_wrap(announcements):
    """
    NEW LISTINGS

    <announcements || "\n\n" {0,3}>

    #ERC20 #gems #EthereumClassic #ICO #Crypto #cryptotrading
    """
    raise NotImplementedError

def reddit_style(token_info):
    """
    **Blah Token $BLAH** by [blah.com](https://blah.com)

    > <description>

    https://confluence-exchange.github.io/#!/trade/BLAH-ETC
    """

    website = get_link(token_info, "Website")
    website_name = urlparse(website).hostname

    symbol = token_info["symbol"] if not "__CONFLUENCEDEX_CUSTOM_SYMBOL" in token_info else token_info["__CONFLUENCEDEX_CUSTOM_SYMBOL"]

    token_name = token_info["name"]
    if "token" not in token_name.lower():
        token_name += " Token"

    description_quote = "> {}".format("\n> ".join(token_info.get("description", "").split("\n")))

    return "**{token_name} ${symbol}** by [{website_name}]({website})  \n{description_quote}\n\nhttps://confluence-exchange.github.io/#!/trade/{symbol}-ETC".format(
        token_name=token_name, symbol=symbol, description_quote=description_quote, website=website, website_name=website_name
    )

def telegram_style(token_info):
    """
    **Blah Token $BLAH** by [blah.com](https://blah.com)

    > <description>

    https://confluence-exchange.github.io/#!/trade/BLAH-ETC
    """

    website = get_link(token_info, "Website")
    website_name = urlparse(website).hostname

    symbol = token_info["symbol"] if not "__CONFLUENCEDEX_CUSTOM_SYMBOL" in token_info else token_info["__CONFLUENCEDEX_CUSTOM_SYMBOL"]

    token_name = token_info["name"]
    if "token" not in token_name.lower():
        token_name += " Token"

    description_quote = "> {}".format("\n> ".join(token_info.get("description", "").split("\n")))

    return "**{token_name} ${symbol}** by {website}  \n{description_quote}\n\nhttps://confluence-exchange.github.io/#!/trade/{symbol}-ETC".format(
        token_name=token_name, symbol=symbol, description_quote=description_quote, website=website, website_name=website_name
    )

def discord_style(token_info):
    """
    **Blah Token $BLAH** by <https://blah.com>
    >

    <https://confluence-exchange.github.io/#!/trade/BLAH-ETC>
    """

    website = get_link(token_info, "Website")
    website_name = urlparse(website).hostname

    symbol = token_info["symbol"] if not "__CONFLUENCEDEX_CUSTOM_SYMBOL" in token_info else token_info["__CONFLUENCEDEX_CUSTOM_SYMBOL"]

    token_name = token_info["name"]
    if "token" not in token_name.lower():
        token_name += " Token"

    description_quote = "> {}".format("\n> ".join(token_info.get("description", "").split("\n")))

    return "**{token_name} ${symbol}** by <{website}>  \n{description}  \n<https://confluence-exchange.github.io/#!/trade/{symbol}-ETC>".format(
        token_name=token_name, description=description_quote, symbol=symbol, website=website
    )


def github_response_style(token_info):
    """
    Thank you for your request! $BLAH token has been listed: https://confluence-exchange.github.io/#!/trade/BLAH-ETC. We will announce it on our channels shortly.

    If you like our project, please consider [donating](https://confluence-exchange.github.io/about/#donate). Your donations keep the project running and are always appreciated.
    """

    symbol = token_info["symbol"] if not "__CONFLUENCEDEX_CUSTOM_SYMBOL" in token_info else token_info["__CONFLUENCEDEX_CUSTOM_SYMBOL"]

    return "Thank you for your request! {name} has been listed: https://confluence-exchange.github.io/#!/trade/{symbol}-ETC".format(name=token_info["name"], symbol=symbol) \
        + "\n\nIf you like our project, please consider [donating](https://confluence-exchange.github.io/about/#donate). Your donations keep the project running and are always appreciated."


STYLE_TO_FUNC = {
    "discord": { "each": discord_style },
    "github_response": { "each": github_response_style },
    "twitter": { "each": twitter_style },
    "twitter_batch": { "each": twitter_short_style, "wrap": twitter_short_wrap },
    "telegram": { "each": telegram_style },
    "reddit": { "each": reddit_style },
}

def main(style, files):
    announcements = []
    for infile in files:
        if os.path.isfile(infile):
            with open(infile, encoding="utf8") as f:
                token_info = yaml.safe_load(f.read())
            announcements.append(STYLE_TO_FUNC[style]["each"](token_info))

    wrap_style = STYLE_TO_FUNC[style]["wrap"] if "wrap" in STYLE_TO_FUNC[style] else print_all_wrap
    wrap_style(announcements)

if __name__ == "__main__":
    import sys
    main(sys.argv[1], sys.argv[2:])
