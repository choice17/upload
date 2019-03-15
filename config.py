class Config(object):
	pass

config = Config()
config.url = 'rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov'
config.scalew = 2100
config.scaleh = 1500
config.debug = 1
config.sleep = [1,2]
config.roi = []
roi1 = [100,100,300,300]
roi2 = [200,200,400,400]
config.roi.append(roi1)
config.roi.append(roi2)


 