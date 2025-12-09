import numpy as np


def generate_lut_histogram(image_data: np.ndarray = None) -> None | np.ndarray | dict[str, np.ndarray]:

    if image_data is None:
        return None
    if len(image_data.shape) == 1:
        mono_lut = np.zeros(256, dtype=np.uint32)

        for pixel_value in image_data:
            mono_lut[pixel_value] += 1

        return mono_lut
    if len(image_data.shape) == 3:
        blue_lut = np.zeros(256, dtype=np.uint32)
        green_lut = np.zeros(256, dtype=np.uint32)
        red_lut = np.zeros(256, dtype=np.uint32)

        blue_channel = image_data[:, :, 0]
        green_channel = image_data[:, :, 1]
        red_channel = image_data[:, :, 2]

        for blue_pixel_value in blue_channel.flat:
            blue_lut[blue_pixel_value] += 1
        for green_pixel_value in green_channel.flat:
            green_lut[green_pixel_value] += 1
        for red_pixel_value in red_channel.flat:
            red_lut[red_pixel_value] += 1

        return {
            'BLUE': blue_lut,
            'GREEN': green_lut,
            'RED': red_lut,
        }