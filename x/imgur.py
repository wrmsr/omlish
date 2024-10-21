"""
https://planspace.org/2013/01/13/upload-images-to-your-imgur-account/

https://api.imgur.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&response_type=pin

curl \
  -X POST \
  -F "client_id=YOUR_CLIENT_ID" \
  -F "client_secret=YOUR_CLIENT_SECRET" \
  -F "grant_type=pin" \
  -F "pin=YOUR_PIN" \
  https://api.imgur.com/oauth2/token

curl \
  -X POST \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "image=@PATH_TO_YOUR_IMAGE_FILE" \
  https://api.imgur.com/3/upload

==

https://stackoverflow.com/questions/64395410/how-can-i-upload-an-image-to-my-account-in-imgur-com-with-curl

curl -X POST -H "Authorization: Bearer YOUR_ACCESS_TOKEN" -F "image=@PATH_TO_YOUR_IMAGE_FILE" https://api.imgur.com/3/upload

curl -X POST -H "Authorization: Bearer 9c9d....9b41f" -F "image=@/tmp/pet.png" https://api.imgur.com/3/upload

{"status":200,"success":true,"data":{"id":"m1Jv","deletehash":"zMI6VN","account_id":2583,"account_url":"ruxr","ad_type":null,"ad_url":null,"title":null,"description":null,"name":"","type":"image/png","width":169,"height":120,"size":3371,"views":0,"section":null,"vote":null,"bandwidth":0,"animated":false,"favorite":false,"in_gallery":false,"in_most_viral":false,"has_sound":false,"is_ad":false,"nsfw":null,"link":"https://i.imgur.com/m1v.png","tags":[],"datetime":16756,"mp4":"","hls":""}}
"""
import os.path
import urllib.error
import urllib.request

from omdev.secrets import load_secrets


def _main() -> None:
    key = load_secrets().get('imgur_client_access_token')

    file = os.path.join(os.path.dirname(__file__), '..', 'ommlx', 'tests', 'test.jpg')
    with open(file, 'rb') as f:
        data = f.read()

    try:
        with urllib.request.urlopen(urllib.request.Request(
            'https://api.imgur.com/3/upload',
            method='POST',
            headers={'Authorization': f'Bearer: {key.reveal()}'},
            data=data,
        )) as resp:
            # url, headers, and status
            print(resp)
    except urllib.error.HTTPError as e:
        print(repr(e))
        print(dict(e.headers))
        print(e.read())
        raise


if __name__ == '__main__':
    _main()
