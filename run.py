#!/usr/bin/python
import YoutubeToMp3

if __name__ == '__main__':
	ytToMp3 = YoutubeToMp3.YoutubeToMP3('xxxxxxxxx', 'your.domain0', 443, '/path/to/cert.pem', '/path/to/key.pem', '/path/to/working-dir')
	ytToMp3.botRun()
