import time
import edgeiq
from edgeiq import realsense


def main():
    obj_detect = edgeiq.ObjectDetection("alwaysai/mobilenet_ssd")
    obj_detect.load(engine=edgeiq.Engine.DNN)

    print("Loaded model:\n{}\n".format(obj_detect.model_id))
    print("Engine: {}".format(obj_detect.engine))
    print("Accelerator: {}\n".format(obj_detect.accelerator))
    print("Labels:\n{}\n".format(obj_detect.labels))
    fps = edgeiq.FPS()

    try:
        with edgeiq.realsense.RealSense() as video_stream, \
                edgeiq.Streamer() as streamer:
            print("Starting RealSense camera")
            time.sleep(2.0)
            fps.start()

            # loop detection
            while True:
                rs_frame = video_stream.read()

                results = obj_detect.detect_objects(
                        rs_frame.image, confidence_level=.5)
                frame = edgeiq.markup_image(
                        rs_frame.image, results.predictions,
                        colors=obj_detect.colors)

                # Generate text to display on streamer
                text = ["Model: {}".format(obj_detect.model_id)]
                text.append(
                        "Inference time: {:1.3f} s".format(results.duration))
                text.append("Objects:")

                for prediction in results.predictions:
                    text.append("{}: {:2.1f}% Distance = {:2.2f}m".format(
                        prediction.label, prediction.confidence * 100,
                        rs_frame.compute_object_distance(
                            prediction.box)))

                streamer.send_data(frame, text)

                fps.update()

                if streamer.check_exit():
                    break

    finally:
        fps.stop()
        print("elapsed time: {:.2f}".format(fps.get_elapsed_seconds()))
        print("approx. FPS: {:.2f}".format(fps.compute_fps()))

        print("Program Ending")


if __name__ == "__main__":
    main()
