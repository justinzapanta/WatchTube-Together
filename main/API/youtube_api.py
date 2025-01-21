from dotenv import load_dotenv

import requests
import os
import json

load_dotenv()

class YoutubeAPI:
    def __init__(self):
        self.url = f'https://www.googleapis.com/youtube/v3'
        self.key = os.getenv('YOUTUBE_APIKEY')

        
    def recommended(self, limit=4, params={'chart' : 'mostPopular', 'part' : 'snippet,contentDetails,statistics'}):
        params['key'] = self.key
        params['maxResults'] = limit
        response = requests.get(f'{self.url}/videos', params=params)
        res_json = response.json()

        result_list = [
            {
                'id' : item['id'],
                'title' : item['snippet']['title'],
                'image' : item['snippet']['thumbnails']['standard']['url']
            }

            for item in res_json['items']
        ]

        return result_list
    

    def search(self, search):
        url = 'https://www.googleapis.com/youtube/v3/search'
        params = {
            'key' : self.key,
            'q' : search,
            'part' : 'snippet',
            'maxResults' : 20
        }

        search_response = requests.get(url, params=params)
        search_json = search_response.json()

        video_ids = ''


        for items in search_json['items']:
            if 'videoId' in items['id']:
                video_ids += f'{items['id']['videoId']},'

        
        params = {
            'key' : self.key,
            'id' : video_ids,
            'part' : 'snippet,contentDetails,statistics,topicDetails',
            'maxResults' : 20
        }

        videos = requests.get('https://www.googleapis.com/youtube/v3/videos', params=params)
        videos_json = videos.json()
        result_list =[]

        for video in videos_json['items']:
            try:
                result_list.append({
                        'id' : video['id'],
                        'title' : video['snippet']['title'],
                        'image' : video['snippet']['thumbnails']['standard']['url'],
                        'channel_title' : video['snippet']['channelTitle'],
                        'published_at' : video['snippet']['publishedAt'],
                        'view_count' : format(int(video['statistics']['viewCount']), ','),
                    })
            except:
                pass

        return result_list


    
    
