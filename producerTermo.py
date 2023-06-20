import PySpin
import matplotlib.pyplot as plt
import keyboard
import pika
import sys
import io
from PIL import Image

continue_recording = True

def handle_close(evt):
    global continue_recording
    continue_recording = False

def run_single_camera(cam):

    try:
        cam.Init()
        global continue_recording
        cam.BeginAcquisition()

        print('Acquiring images...')

        image_result = cam.GetNextImage()

        if image_result.IsIncomplete():
            print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

        else:
            image_data = image_result.GetNDArray()
            image_data_celsius = image_data * 0.04 - 273.15
            fig, ax = plt.subplots()
            ax.imshow(image_data_celsius, cmap='inferno')
            output_path = "last_send_file.jpeg"
            fig.savefig(output_path)
            plt.pause(0.001)
            plt.clf()

            if keyboard.is_pressed('ENTER'):
                print('Program is closing...')
                plt.close('all')
                input('Done! Press Enter to exit...')
                continue_recording = False

        image_result.Release()
        cam.EndAcquisition()
        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False


def main():
    result = True

    system = PySpin.System.GetInstance()
    cam_list = system.GetCameras()
    num_cameras = cam_list.GetSize()

    if num_cameras == 0:
        cam_list.Clear()
        system.ReleaseInstance()
        print('Not enough cameras!')
        return False

    cam = cam_list[0]
    run_single_camera(cam)
    del cam
    cam_list.Clear()
    system.ReleaseInstance()

    byteIO = io.BytesIO()
    img = Image.open("last_send_file.jpeg")
    img.save(byteIO, format='JPEG')

    byteArr = byteIO.getvalue()

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='topic', exchange_type='topic')
    routing_key = sys.argv[1] if len(sys.argv) > 2 else 'anonymous.info'

    channel.basic_publish(exchange='topic', routing_key=routing_key, body=byteArr)
    print(" [Image] Sent %r" % (routing_key))
    connection.close()

    input('Done! Press Enter to exit...')
    return result

if __name__ == '__main__':
    main()