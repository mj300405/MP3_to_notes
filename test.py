import os
#os.environ["VLC_PLUGIN_PATH"] = "/usr/lib/vlc/plugins"
import vlc

player = vlc.MediaPlayer("https://www.example.com/test.mp3")
player.play()