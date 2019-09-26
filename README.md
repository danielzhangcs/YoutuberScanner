# Youtuber-Scanner

A search engine that helps users find the most relevant youtube creator based on the users' queries.

Team member: Daniel Zhang, He Zhang, Shangyu Zhang(Team Leader)

Links:
* [Presentation0](https://docs.google.com/presentation/d/1aTelL0VpH3ryxLJ1KtqgPeXJ0-PFoh5SoMjn1s0e_q8/edit?usp=sharing)
* [Presentation1](https://docs.google.com/presentation/d/1GX61ccG3XShJF-RaaorWcl0rJkzyEUTFnD975_GIYQk/edit?usp=sharing)

## Design

This project involves 2 parts: a web UI and a backend.

The web UI will parse users' queries, then trigger correct intent, which will then handled by backend, generating proper response.

## Data

Channels corpus data is too large to push to Github.
Therefore, please download the corpus data here - https://drive.google.com/file/d/1J4YLH-R20ZAW7mTqAi7Wo7szSbhWqgZ2/view?usp=sharing

However, recently, we just updated our data corpus. Please download the fixed corpus data here - https://drive.google.com/open?id=1S04TH_kIi-LbslJqfHujSAxPExWbSGiY


Then, put it under folder `data/`.

Youtuber's channels data will be composed of structured data and unstructured data like:
```
{
    "UC1zZE_kJ8rQHgLTVfobLi_g": {
        "channel_create_date": "2010-01-04", 
        "view_count": 2306511170, 
        "video_count": 908, 
        "channel_title": "The King of Random", 
        "subscriber_count": 11231689, 
        "all_playlists_titles": "King Of Random Rewind Slime Time Ice, Ice Baby Molten Mayhem Things that Go BOOM!", 
        "all_playlists_desc": "Cool things you can make using common household materials. Crazy experiments with gummy candy, chocolate, and homemade silicone molds.", 
        "channel_id": "UC1zZE_kJ8rQHgLTVfobLi_g", 
        "channel_desc": "We make videos dedicated to exploring life through all kinds of life hacks, experiments, and random weekend projects.\n\nThere is excitement found in discovering the unknown, so join us and let\u2019s build something great together. \n\nFTC Disclaimer: We earn a % of sales made through Amazon Affiliate links", 
        "image_url": "https://yt3.ggpht.com/a/AGF-l7903sDCe8kkmFFSKhznQOho6fTemCuw_f3zHg=s88-mo-c-c0xffffffff-rj-k-no", 
        "latest_upload_datetime": "2019-04-12",
        "like_over_dislike": 36.8,
        "upload_interval": 12.839080459770114, 
        "all_videos_desc": "Compilation Playlist: I'd drank earlier, and therefore more clear in color. In either case, I have the same success igniting tinder with either liquid lens so the difference made by the color is negligible.", 
        "channel_url": "https://www.youtube.com/channel/UC1zZE_kJ8rQHgLTVfobLi_g", 
        "categories": [
            "https://en.wikipedia.org/wiki/Lifestyle_(sociology)", 
            "https://en.wikipedia.org/wiki/Food"
        ], 
        "all_videos_titles": "10 Things You Should Make This Weekend\n| Rewind #1 10 Things You Can Make At Home | Rewind #2 10 EASY DIY Projects | Rewind #3 Electric Pickles and Vacuum Slime | Rewind #4 Glass Bottle Arrowheads & Breathing Fire | Rewind #5  Glow Oobleck Monster Mosh Pit Magnetic Slime Swallowing Monster Magnets DIY Unicorn Snot Shooting Slime with the Flamethrower Slime In a Vacuum Chamber  DIY Dry Ice Soda Slushies How To Make RAINBOW Instant Ice! Mixing Dry Ice with Molten Salt The Ice Experiments: Molten Brass Deep Frying Dry Ice  When Molten Salt Hits Molten Metal The Ice Experiments: Molten Copper The Ice Experiments: Molten Fidget Spinners The Ice "
    },
    "UC1zZE_kJ8rQHgLTVfobLi_g": {
        "channel_create_date": "2010-01-04", 
        "view_count": 2306511170, 
        ...
    },
    ...
}
```

## Backend Setups

### Install Dependency

```bash
# install virtualenv to easily manage python versions
pip3 install virtualenv 

# Create your own ENV like
virtualenv ENV

# Source your ENV
source ENV\bin\activate

# Install packages by typing
pip3 install -r requirements.txt
```

### Run

To run backend:
1. Enable the correct python virtual env
2. `sudo -i service elasticsearch start`
3. `python3 index.py`
4. `python3 main.py`
5. Open your browser and go to http://127.0.0.1:5000

A flask server will run on port 5000.
