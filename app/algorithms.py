# algorithms.py
import math

import numpy as np


# Dla Lab1 - zadanie 2
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


# Dla Lab1 - zadanie 3
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


# Dla Lab1 - zadanie 3
def linear_saturation_streching_histogram(image_data: np.ndarray):
    """
    Rozciąganie liniowe z przesyceniem (5%)
    Ucina 2.5% najciemniejszych i 2.5% najjaśniejszych pikseli

    Zoptymalizowany wzór:
    nowy_pixel = (stary_pixel - próg_dolny) * 255 / (próg_górny - próg_dolny)

    :param image_data: np.ndarray zdjęcie cv2
    :return: zwraca nowe zdjęcie
    """

    # Definicja pod nowy canvas
    height = image_data.shape[0]
    width = image_data.shape[1]

    # Kopia obrazu
    new_image = np.zeros_like(image_data)

    if len(image_data.shape) == 2:
        print("Rozciąganie z saturacją - Szare")

        # Wyliczenie progu dolnego
        min_threshold = np.percentile(image_data, 2.5)

        # Wyliczenie progu górnego
        max_threshold = np.percentile(image_data, 97.5)

        if min_threshold == max_threshold:
            return image_data

        scale = 255 / (max_threshold - min_threshold)

        # Pętla po wierszach
        for y in range(height):
            # Pętla po kolumntach
            for x in range(width):
                # Wartość starego pixela
                old_pixel = image_data[y, x]

                # Nowy pixel wg wzoru. Zamieniam na float, aby podczas obliczeń nie ucinać mnożenia np. dla 2.5,
                # może uciąć do 2
                new_pixel = (float(old_pixel) - min_threshold) * scale

                # Zapobieganie liczbom większym 255 i mniejszym niż 0
                new_pixel = np.clip(new_pixel, 0, 255)

                # Przypisanie do nowego obrazu oraz konwercja do int
                new_image[y, x] = int(new_pixel)

                # BGR
    elif len(image_data.shape) == 3:
        print("Rozciąganie liniowe - Kolorowe")
        channels = image_data.shape[2]

        for c in range(channels):
            # Iteracja po kanałach

            # Wyliczenie progów
            current_channel_data = image_data[:, :, c]
            # Wyliczenie progu dolnego
            min_threshold = np.percentile(current_channel_data, 2.5)
            # Wyliczenie progu górnego
            max_threshold = np.percentile(current_channel_data, 97.5)

            # Zabezpieczenie
            if max_threshold == min_threshold:
                scale = 0
            else:
                # Obliczenie drugiej części wzoru
                scale = 255.0 / (max_threshold - min_threshold)

            # Iteracja po wierszach
            for y in range(height):
                # Iteracja po kolumnach
                for x in range(width):
                    old_pixel = image_data[y, x, c]

                    # Nowy pixel wg wzoru. Zamieniam na float, aby podczas obliczeń nie ucinać mnożenia np. dla 2.5,
                    # może uciąć do 2
                    new_pixel = (float(old_pixel) - min_threshold) * scale

                    # Zapobieganie liczbom większym 255 i mniejszym niż 0
                    new_pixel = np.clip(new_pixel, 0, 255)

                    # Przypisanie do nowego obrazu oraz konwercja do int
                    new_image[y, x, c] = int(new_pixel)

    return new_image


# Dla Lab1 - zadanie 3
def histogram_equalization(image_data: np.ndarray):
    """
    Wyrównanie histogramu (Equalizacja).

    Wzór na obliczenie nowego pixel-a:

    licznik = aktualna_dystrybuanta - wyliczona_minimalna_dystrybuanta
    mianownik = ilość_wszystkich_pixeli - wyliczona_minimalna_dystrybuanta

    nowy_pixel = (licznik / mianownik) * maxymalna_dostępna_jasność

    Algorytm:

    1. Potrzebna tablica lut. Generowanie za pomocą funkcji generate_lut_histogram
    2. Na tablicy lut_histogram wykonuję sumę narastającą (nowa tabela) w celu użycia wartości w każdym punkcie pod
        wzór na nową wartość jasności
    3. Znalezienie dystrybuanty minimalnej, czyli miejsca w tablicy sumy narastającej gdzie jest pierwsza wartość
        niezerowa
    4.  Na tablicy sumy narastającej wykonuję pętlę ze wzorem iwpisuję tę wartość do nowej tablicy lut zawierającą
        przekształcenie
    5. Na podstawie nowej tablicy lut wykonuję przekształcenie na cały obrazie pixel po pixelu, np. pixel o wartości 5
        zmienia się w pixel o wartości 15, jeżeli w nowej tablicy lut nowa_tablica_lut[5] = 15
    """

    height, width = image_data.shape[:2]    # do obliczenia total_pixel do wzoru oraz na pętlę
    total_pixels = height * width           # mianownik wzoru
    new_image = np.zeros_like(image_data)   # zarezerwowanie pamięci na nowy obrazek

    # Szaroodcieniowy
    if len(image_data.shape) == 2:
        print("Equalizacja - Szaroodcieniowe")

        # Punkt 1 algorytmu
        lut_hist = generate_lut_histogram(image_data)

        # Punkt 2 algorytmu
        cdf_array = np.zeros(int(len(lut_hist)))

        for brightness, contu in enumerate(lut_hist):
            if brightness == 0:
                cdf_array[brightness] = lut_hist[brightness]
            else:
                cdf_array[brightness] = cdf_array[brightness - 1] + lut_hist[brightness]

        # Punkt 3 algorytmu
        cdf_min = 0
        for value in cdf_array:
            if value > 0:
                cdf_min = value
                break

        # Punkt 4 algorytmu
        new_lut_table = np.zeros(int(len(lut_hist)))

        for index, cdf in enumerate(cdf_array):
            new_lut_table[index] = ((cdf_array[index] - cdf_min) / (total_pixels - cdf_min)) * 255

        # Punkt 5 algorytmu
        # Iteracja po wierszach pixeli obrazu
        for x in range(height):
            # Iteracja po kolumnach pixeli obrazu
            for y in range(width):
                current_pixel_value = image_data[x, y]
                new_pixel_value = new_lut_table[current_pixel_value]
                new_image[x, y] = new_pixel_value

    # Kolorowy
    if len(image_data.shape) == 3:
        print("Equalizacja - Kolorowe")

        # Dla każdego kanału należy obliczyć nową wartość, a nie dla ich sumy
        for channel in range(image_data.shape[2]):

            # Punkt 1 algorytmu
            lut_hist = generate_lut_histogram(image_data[:, :, channel])

            # Punkt 2 algorytmu
            cdf_array = np.zeros(int(len(lut_hist)))

            for brightness, contu in enumerate(lut_hist):
                if brightness == 0:
                    cdf_array[brightness] = lut_hist[brightness]
                else:
                    cdf_array[brightness] = cdf_array[brightness - 1] + lut_hist[brightness]

            # Punkt 3 algorytmu
            cdf_min = 0
            for value in cdf_array:
                if value > 0:
                    cdf_min = value
                    break

            # Punkt 4 algorytmu
            new_lut_table = np.zeros(int(len(lut_hist)))

            for index, cdf in enumerate(cdf_array):
                new_lut_table[index] = ((cdf_array[index] - cdf_min) / (total_pixels - cdf_min)) * 255

            # Punkt 5 algorytmu
            # Iteracja po wierszach pixeli obrazu
            for x in range(height):
                # Iteracja po kolumnach pixeli obrazu
                for y in range(width):
                    current_pixel_value = image_data[x, y, channel]
                    new_pixel_value = new_lut_table[current_pixel_value]
                    new_image[x, y, channel] = new_pixel_value

    return new_image


# Dla Lab1 - zadanie 4
def point_negation(image_data: np.ndarray):
    """
    Wzór na negację
    nowy_pixel = 255 - stary_pixel
    :param image_data: tablica z danym obrazu
    :return: Zwraca nowy obraz
    """

    # Biblioteka numpy odejmuje 255 od każdego elementu w tablicy
    return 255 - image_data


# Dla Lab1 - zadanie 4
def point_posterize(image_data: np.ndarray, levels: int):
    """
    Redukcja poziomów szarości (posteryzacja)
    Dzieli zakres 0-255 na podaną przez użytkownika ilość kawałków

    Algorytm:
    1. Dzielę zakres jasności 255 na tyle poziomów, ile chce użytkownik

        Wzór do wyliczenia progów:
        255 / (levels - 1)
    2. Na każdym pixelu wykonuję operację sprawdzenia, do jakiego zakresu wpada dany pixel i przypisuję mu odpowiedą
        nową wartość

        Wzór do wyliczenia, do jakiego zakresu wpada pixel:
        index_zakresu = floor((stary_pixel * levels) / 256)


    :param image_data: tablica z danym obrazu
    :param levels: podany przez użytkownika numer
    :return: Zwraca nowy obraz
    """
    height, width = image_data.shape[:2]
    new_image = np.zeros_like(image_data)

    # Szaroodcieniowe
    if len(image_data.shape) == 2:
        print("Posteryzacja - Szaroodcieniowe")
        # Punkt 1 algorytmu
        steps = np.zeros(levels)

        for index in range(len(steps)):
            steps[index] = int((255 / (levels - 1)) * index)

        # Punkt 2 algorytmu
        for x in range(height):
            for y in range(width):
                # Przepisuję do zmiennej z int() ponieważ dane są w uint8, czyli podczas mnożenia
                # dostanę resztę z dzielenia
                old_pixel_value = int(image_data[x, y])
                step = math.floor((old_pixel_value * levels) / 256)
                new_image[x, y] = steps[step]

    if len(image_data.shape) == 3:
        print("Posteryzacja - Kolorowe")

        for channel in range(image_data.shape[2]):
            # Punkt 1 algorytmu
            steps = np.zeros(levels)

            for index in range(len(steps)):
                steps[index] = int((255 / (levels - 1)) * index)

            # Punkt 2 algorytmu
            for x in range(height):
                for y in range(width):
                    # Przepisuję do zmiennej z int() ponieważ dane są w uint8, czyli podczas mnożenia dostanę
                    # resztę z dzielenia
                    old_pixel_value = int(image_data[x, y, channel])
                    step = math.floor((old_pixel_value * levels) / 256)
                    new_image[x, y, channel] = steps[step]

    return new_image


# Dla Lab1 - zadanie 4
def point_binary_threshold(image_data: np.ndarray, threshold: int):
    """
    Progowanie binarne

    Algorytm:
    Jeżeli, pixel > od progu = 255
    Jeżeli, pixel < od progu = 0
    :param image_data: tablica ndarray zwierająca dane obrazu
    :param threshold: próg podany przez użytkownika
    :return: zwraca nowy obraz
    """
    # Biblioteka numpy dla każdego elementu wykonuje operację:
    # np.where(warunek, jeżeli_tak, jeżeli_nie)
    # dodatkowo należy dodać typ, w jakim zostanie zwrócona wartość
    return np.where(image_data > threshold, 255, 0).astype(np.uint8)


# Dla Lab1 - zadanie 4
def point_keep_gray_threshold(image_data: np.ndarray, threshold: int):
    """
    Progowanie z zachowaniem poziomów szarości

    Algorytm:
    Jeżeli pixel > próg = zostawiam bez zmian
    Jeżeli pixel < próg = 0
    :param image_data: tablica ndarray zwierająca dane obrazu
    :param threshold: próg podany przez użytkownika
    :return: zwraca nowy obraz
    """

    return np.where(image_data > threshold, image_data, 0).astype(np.uint8)