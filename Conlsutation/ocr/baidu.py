from aip import AipOcr

APP_ID = '16657913'
API_KEY = 'SNbBvp0R4Lbu6DqssoTnUGc0'
SECRECT_KEY = 'hp4tO0XDGDSFZ5tLbSbV68qgDvn4fENL'
client = AipOcr(APP_ID, API_KEY, SECRECT_KEY)


def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


options = {"detect_language": "true", 'language_type': "CHN_ENG"}
image = get_file_content('./img/xt.jpg')
message = client.basicAccurate(image)
print(message)
