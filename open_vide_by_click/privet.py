import os #это база
import subprocess # pip install subprocess.run
import ctypes #pip install ctypes

def play_video(file_path):
    vlc_path = "VLCportable\\VLCportable" #путь к vlc (в конце указываю сам exe)
    subprocess.Popen([vlc_path, '--fullscreen', file_path]) # тут все норм

def wait_for_middle_click():
    while True:
        if ctypes.windll.user32.GetAsyncKeyState(0x04):
            return True

if __name__ == "__main__":
    video_path = os.path.join(os.path.dirname(__file__), 'privet.mp4') #файл и код в одну папку чтобы не указывать путь

    wait_for_middle_click()

    play_video(video_path)

