# algorithms.py
import numpy as np


def generate_lut_histogram(image_data: np.ndarray = None) -> None | np.ndarray | dict[str, np.ndarray]:
    """Funkcja generująca tablicę lut dla histogramu"""

    if image_data is None:
        return None

    # Szaro-odcieniowy
    if len(image_data.shape) == 2:
        mono_lut = np.zeros(256, dtype=np.uint32)

        for pixel_value in image_data.flat:
            mono_lut[pixel_value] += 1

        return mono_lut

    # RGB
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
            'blue': blue_lut,
            'green': green_lut,
            'red': red_lut,
        }


def linear_streching_histogram(image_data: np.ndarray):
    """
    Funkcja przyjmuje originalny obraz (image_data) i wykonuje operacje rozciągnięcia liniowego
    Najciemniejszy pixels staje się czarny a najaśniejszy biały

    Wzór:
    Nowy pixel = (stary_pixel - wartość_minimalna) / (wartość_maksymalna - wartość_minimalna) * zakres_jasności

    Zoptymalizowany wzór
    Nowy pixel = (stary_pixel - wartość_minimalna) * (255 / wartość_maksymalna - wartość_minimalna)

    :param image_data: tablica numpy z obrazem
    :return: zwraca nową np.ndarray
    """

    # Definicja pod nowy canvas
    height = image_data.shape[0]
    width = image_data.shape[1]

    # Kopia obrazu
    new_image = np.zeros_like(image_data)

    # Szaroodcieniowy
    if len(image_data.shape) == 2:
        print("Rozciąganie liniowe - Szaroodcieniowe")

        min_value = np.min(image_data)
        max_value = np.max(image_data)

        if min_value == max_value:
            return image_data

        scale = 255 / (max_value - min_value)

        # Pętla po wierszach
        for y in range(height):
            # Pętla po kolumntach
            for x in range(width):
                # Wartość starego pixela
                old_pixel = image_data[y, x]

                # Nowy pixel wg wzoru. Zamieniam na float, aby podczas obliczeń nie ucinać mnożenia np. dla 2.5,
                # może uciąć do 2
                new_pixel = (float(old_pixel) - min_value) * scale

                # Przypisanie do nowego obrazu oraz konwercja do int
                new_image[y, x] = int(new_pixel)

                # BGR
    elif len(image_data.shape) == 3:
        print("Rozciąganie liniowe - Kolorowe")
        channels = image_data.shape[2]

        for c in range(channels):
            # Iteracja po kanałach

            # Wyliczenie maksymalnej i minimalnej wartości dla jednego z 3 kanałów
            current_channel_data = image_data[:, :, c]
            min_value = np.min(current_channel_data)
            max_value = np.max(current_channel_data)

            # Zabezpieczenie
            if max_value == min_value:
                scale = 0
            else:
                # Obliczenie drugiej części wzoru
                scale = 255.0 / (max_value - min_value)

            # Iteracja po wierszach
            for y in range(height):
                # Iteracja po kolumnach
                for x in range(width):
                    old_pixel = image_data[y, x, c]

                    # Nowy pixel wg wzoru. Zamieniam na float, aby podczas obliczeń nie ucinać mnożenia np. dla 2.5,
                    # może uciąć do 2
                    new_pixel = (float(old_pixel) - min_value) * scale

                    # Przypisanie do nowego obrazu oraz konwercja do int
                    new_image[y, x, c] = int(new_pixel)

    return new_image
