# algorithms.py
import math

import cv2
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

    height, width = image_data.shape[:2]  # do obliczenia total_pixel do wzoru oraz na pętlę
    total_pixels = height * width  # mianownik wzoru
    new_image = np.zeros_like(image_data)  # zarezerwowanie pamięci na nowy obrazek

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


# Dla Lab2 - zadanie 1
def check_compatibility(img1: np.ndarray, img2: np.ndarray) -> bool:
    """Sprawdza, czy obrazy mają ten sam rozmiar i liczbę kanałów"""

    if img1 is None or img2 is None:
        return False
    # .shape zwraca krotkę (wysokość, szerokość, kanały)
    # operator porównania porównuje krotki między sobą (ich wartości)
    return img1.shape == img2.shape


# Dla Lab2 - zadanie 1
def multi_image_addition(images: list[np.ndarray], saturate: bool = True):
    """
    Algorytmy:
    Dla saturacji pozytywnej:
    Dodaję tablicę obrazów do siebie i na końcu obcinam wszystkie wartości do maksymalnej jasności

    Dla saturacji negatywnej, czyli uśrednienie:
    Dodaję również każdą tablicę do siebie, ale wartości każdej z nich dzielę przez ilość przekazanych obrazów,
    dzięki czemu nie tracę danych podczas ucinania, ponieważ ucinać nie trzeba.

    Funkcja dodająca obrazy do siebie
    :param images: przekazana lista zdjęć z dialogu
    :param saturate: True: Suma i obcięcie do 255, False: Uśrednianie, czyli skalowanie wagowe z uniknięciem wysycenia
    :return: Zwraca gotowy obraz
    """

    if not images:
        return None

    # Walidacja rozmiarów
    reference_image = images[0]

    # Iteracja po liście zdjęć bez pierwszeg o porównanie ich między sobą
    for index, image in enumerate(images[1:]):
        if not check_compatibility(reference_image, image):
            raise ValueError(f"Niezgodność rozmiarów! Pierwszy przekazany obraz ma {reference_image.shape}. Przekazany "
                             f"{index + 2} obraz ma wymiar {image.shape}")

    # Konwertuję na float dla precyzji obliczeń
    result_image_float = np.zeros_like(reference_image, dtype=np.float32)

    images_count = len(images)

    # Dla wysycenia
    if saturate:
        # Zsumowanie wartości
        for image in images:
            result_image_float += image.astype(np.float32)

        # Obcięcie wartości nadmiarowych
        result_image_float = np.clip(result_image_float, 0, 255)

    # Bez wysycenia
    if not saturate:
        # Zsumowanie wartości, ale podzielenie przez sumę przekazanych obrazów
        for image in images:
            result_image_float += (image.astype(np.float32) / images_count)

        # Dla pewności klipuję
        result_image_float = np.clip(result_image_float, 0, 255)

    # Konwertuję na odpowiedni typ danych
    result_image_uint8 = result_image_float.astype(np.uint8)

    return result_image_uint8


# Dla Lab2 - zadanie 1
def scalar_operation(image_data: np.ndarray, value: int, operation: str, saturate: bool):
    """
    Operacje skalarne, czyli wykonanie operacji matematycznych na jasności obrazu np. dodawanie, odejmowanie, dzielenie,
    ale z użyciem liczby

    :param image_data: przekazany obraz
    :param value: wartość, o którą należy zmienić obraz
    :param operation: 'add', 'multiply', 'division'
    :param saturate: True / False
    :return: zwraca nowy obraz
    """
    # Przepisanie obrazu ze zmianą typu danych dla dokładniejszych obliczeń matematycznych
    image_float = image_data.astype(np.float32)
    result_image = None

    if image_data is None:
        return None

    if operation == 'addition':
        if saturate:
            # Tutaj dodaję a na końcu i tak klipuję każdą operację
            result_image = image_float + value
        else:
            result_image = (image_float * 0.5) + (value * 0.5)

    elif operation == 'multiplication':
        if saturate:
            result_image = image_float * value
        else:
            # Obraz wynikowy się nie zmieni, ale to dodaję ze względu na uwagę
            result_image = (image_float / value) * value
    elif operation == 'division':
        if value == 0:
            return image_float  # Nie można dzielić przez 0

        # Nie potrzeba if-a dla saturacji, ponieważ wartości podczas dzielenia nigdy nie przekroczy 255
        result_image = image_float / value

    result_image = np.clip(result_image, 0, 255)
    return result_image.astype(np.uint8)


# Dla Lab2 - zadanie 1
def absolute_difference(image1: np.ndarray, image2: np.ndarray):
    """
    Różnica bezwzględna dwóch zdjęć
    :param image1: zdjęcie 1
    :param image2: zdjęcie 2
    :return: zwraca gotowe zdjęcie po operacji
    """
    if not check_compatibility(image1, image2):
        raise ValueError("Obrazy muszą mieć ten sam rozmiar i razem być kolorowe lub szaroodcieniowe")

    # Zamieniam, aby mieć dostęp do liczb ujemnych
    image1_float = image1.astype(np.float32)
    image2_float = image2.astype(np.float32)

    # Odejmuję obrazy od siebie
    diff = image1_float - image2_float

    # Z wartości ujemnych robię dodatnie
    absolute_diff = np.abs(diff)

    # Zwracam gotowy obraz z odpowiednią konwersją
    return absolute_diff.astype(np.uint8)


# Dla Lab2 - zadanie 2
def logical_operation(image1: np.ndarray, image2: np.ndarray | None, operation: str):
    """
    Operacje logiczne na bitach (per pixel): NOT, AND, OR, XOR
    :param image1: zdjęcie 1
    :param image2: zdjęcie 2
    :param operation: wybrana operacja przez użytkownika
    :return: zwraca gotowy obraz
    """

    # Operacja negacji
    if operation == 'not':
        # np.bitwise: odwraca bity
        return np.bitwise_not(image1)

    # Walidacja dla operacji z dwoma zdjęciami
    if image2 is None:
        raise ValueError("Ta operacja wymaga drugiego obrazu!")

    if not check_compatibility(image1, image2):
        raise ValueError(f"Niezgodność rozmiarów lub typów obrazów! Obraz 1: {image1.shape}, Obraz 2: {image2.shape}")

    if operation == 'and':
        # Koniunkcja bitowa, dla maskowania na przykład
        return np.bitwise_and(image1, image2)

    elif operation == 'or':
        # Alternatywan bitowa: łączenie dwóch obrazów w jeden
        return np.bitwise_or(image1, image2)

    elif operation == 'xor':
        # Alternatywa z wykluczeniem, wynik jest 1 tylko, gdy bity wejściowe są od siebie różne
        # Używane do wykrycia zmian między obrazami
        return np.bitwise_xor(image1, image2)

    else:
        raise ValueError(f"Nieznana operacja logiczna: {operation}")


def convert_to_binary_mask(image: np.ndarray) -> np.ndarray:
    """
    Konwerscja maski logicznej (0-1) na obraz 8-bitowy (0-255)
    Zamieniam obraz 8-bitowy na obraz binarny, aby wykonać na nim operację.
    :param image:
    :return:
    """
    return np.where(image > 0, 1, 0).astype(np.uint8)


def convert_to_8bit_mask(image: np.ndarray) -> np.ndarray:
    """
    Konwerscja maski logicznej (0-1) na obraz 8-bitowy (0-255)
    Zamieniam obraz binarny, na którym wykonałem operację na obraz 8-bitowy do wyświetlenia na ekranie
    :param image:
    :return:
    """
    return np.where(image > 0, 255, 0).astype(np.uint8)


# Dla Lab2 - zadanie 3
KERNELS = {
    # Maski dla wygładzania
    "Wygładzanie": {
        "Uśrednienie 3x3": np.array([
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1]
        ], dtype=np.float32) / 9.0,  # Każda liczba w macierzy będzie podzielona przez 9
        "Uśrednienie (5x5)": np.array([
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1]
        ], dtype=np.float32) / 25.0,  # Każda liczba w macierzy będzie podzielona przez 25
        "Maska z wagami (3x3)": np.array([
            [1, 2, 1],
            [2, 4, 2],
            [1, 2, 1]
        ], dtype=np.float32) / 16.0,
        # To samo co wyżej
        "Gauss (3x3)": np.array([
            [1, 2, 1],
            [2, 4, 2],
            [1, 2, 1]
        ], dtype=np.float32) / 16.0,
        "Gauss (5x5)": np.array([
            [1, 4, 7, 4, 1],
            [4, 16, 26, 16, 4],
            [7, 26, 41, 26, 7],
            [4, 16, 26, 16, 4],
            [1, 4, 7, 4, 1]
        ], dtype=np.float32) / 273.0,
    },

    # Maski dla wyostrzania
    "Wyostrzanie": {
        # Wyostrzenie lekki
        "Maska 1": np.array([
            [0, 1, 0],
            [1, -4, 1],
            [0, 1, 0]
        ], dtype=np.float32),
        # Wyostrzenie mocne
        "Maska 2": np.array([
            [1, 1, 1],
            [1, -8, 1],
            [1, 1, 1]
        ], dtype=np.float32),
        # To samo co pierwsze tylko zmieniony środek dla łatwości matematycznej
        "Maska 3": np.array([
            [0, -1, 0],
            [-1, 4, -1],
            [0, -1, 0]
        ], dtype=np.float32),
    },

    "Detekcja Krawędzi - Prewitt": {
        "N": np.array([
            [1, 1, 1],
            [0, 0, 0],
            [-1, -1, -1]
        ], dtype=np.float32),
        "NE": np.array([
            [0, 1, 1],
            [-1, 0, 1],
            [-1, -1, 0]
        ], dtype=np.float32),
        "E": np.array([
            [-1, 0, 1],
            [-1, 0, 1],
            [-1, 0, 1]
        ], dtype=np.float32),
        "SE": np.array([
            [-1, -1, 0],
            [-1, 0, 1],
            [0, 1, 1]
        ], dtype=np.float32),
        "S": np.array([
            [-1, -1, -1],
            [0, 0, 0],
            [1, 1, 1]
        ], dtype=np.float32),
        "SW": np.array([
            [0, -1, -1],
            [1, 0, -1],
            [1, 1, 0]
        ], dtype=np.float32),
        "W": np.array([
            [1, 0, -1],
            [1, 0, -1],
            [1, 0, -1]
        ], dtype=np.float32),
        "NW": np.array([
            [1, 1, 0],
            [1, 0, -1],
            [0, -1, -1]
        ], dtype=np.float32),
    },

    "Detekcja krawędzi - Sobel": {
        "Sobel X": np.array([
            [-1, 0, 1],
            [-2, 0, 2],
            [-1, 0, 1]
        ], dtype=np.float32),
        "Sobel Y": np.array([
            [-1, -2, -1],
            [0, 0, 0],
            [1, 2, 1]
        ], dtype=np.float32),
    }
}


def apply_linear_filter(image: np.ndarray, kernel: np.ndarray, border_type: int, border_value: int):
    """
    Funkcja nagkładająca wykonująca operację na macierzy za pomocą przekazanej macierzy
    :param image: przekazane zdjęcie
    :param kernel: wybrana macierz do wykonania operacji
    :param border_type: typ uzupełnienia krawędzi zdjęcia
    :param border_value określa, z jaką wartością ma być wypełniona ramka lub jaką wartość marginesów ma brać
    :return: zwraca nowe zdjęcie
    """
    padding_height = kernel.shape[0] // 2  # dzielenie całkowite przez 2
    padding_width = kernel.shape[1] // 2  # dzielenie całkowite przez 2

    # Wypełnienie ramki stałą wartością n.
    # 9999 dla BORDER_OVERWRITE
    if border_type == 9999:
        result_image = cv2.filter2D(src=image, ddepth=-1, kernel=kernel, borderType=cv2.BORDER_REPLICATE)

        # Nadpisanie ramki
        if padding_height > 0:
            # Nadpisuję do x np. 1 i wszystkie kolumny
            result_image[:padding_height, :] = border_value
            # Nadpisuję od x np. -1 - czyli od przedostatniego elementu do końca i wszystkie kolumny
            result_image[-padding_height:, :] = border_value
        if padding_width > 0:
            # Wszystkie wiersze i do np. 1 kolumny y
            result_image[:, :padding_width] = border_value
            # Wszsytkie wiersze i od np. przed ostatniego do końca
            result_image[:, -padding_width:] = border_value

        return result_image

    # Obramówka stała
    elif border_type == cv2.BORDER_CONSTANT:
        # Powiększam zdjęcie o margines jasności podanej przez użytkownika
        padded_image = cv2.copyMakeBorder(
            image,
            top=padding_height, bottom=padding_height, left=padding_width, right=padding_width,
            borderType=cv2.BORDER_CONSTANT,
            value=border_value
        )
        # Wykonuję operacje na powiększonym zdjęciu
        result_padded_image = cv2.filter2D(src=padded_image, ddepth=-1, kernel=kernel, borderType=border_type)

        # Zwracam kopie wyciętego obrazka. Wyciętego dlatego, aby zachował oryginalny rozmiar.
        return result_padded_image[padding_height: -padding_height, padding_width:-padding_width].copy()

    # W wypadku BORDER_REFLECT po prostu przekazuję to do metody opencv
    else:
        return cv2.filter2D(src=image, ddepth=-1, kernel=kernel, borderType=border_type)


def apply_laplacian_sharpening(image: np.ndarray, kernel: np.ndarray, border_type: int, border_value: int):
    """
    Funkcja nagkładająca wykonująca operację na macierzy za pomocą przekazanej macierzy

    Algorytm:
    Obraz wyostrzony = obraz oryginalny + wykryte krawędzie

    :param image: przekazane zdjęcie
    :param kernel: wybrana macierz do wykonania operacji
    :param border_type: typ uzupełnienia krawędzi zdjęcia
    :param border_value określa, z jaką wartością ma być wypełniona ramka lub jaką wartość marginesów ma brać
    :return: zwraca nowe zdjęcie
    """
    # Konwersja podobnie jak w funkcjach powyżej, aby nie tracić wartości ujemnych przy filtracji
    image_float = image.astype(np.float32)

    # Sprawdzenie, jaka jest wartość środkowa
    center_value = kernel[1, 1]

    padding_height = kernel.shape[0] // 2  # dzielenie całkowite przez 2
    padding_width = kernel.shape[1] // 2  # dzielenie całkowite przez 2

    # Wypełnienie ramki stałą wartością n.
    # 9999 dla BORDER_OVERWRITE
    if border_type == 9999:

        # Obliczenie krawędzi
        # cv2.CV_32F to jest oznaczenie typu pamięci, jakie ma wykorzystać opencv
        # Wyżej przekonwertowałem do float32 więc tutaj muszę też użyć float32
        edges = cv2.filter2D(image_float, cv2.CV_32F, kernel, borderType=cv2.BORDER_REPLICATE)

        # Jeżeli środek macierzy jest na minusie -4 to odejmuję krawędzie,
        # ponieważ edges zawiera krawędzie jako wartości
        # ujemne, więc żeby je dodać do obrazu należy odjąć
        if center_value < 0:
            result_image = image_float - edges
        # Na odwró†
        else:
            result_image = image_float + edges

        # Ucinam mniejsze od zera i większe od 255
        result_image_clipped = np.clip(result_image, 0, 255).astype(np.uint8)

        # Nadpisanie ramki
        if padding_height > 0:
            result_image_clipped[:padding_height, :] = border_value
            result_image_clipped[-padding_height:, :] = border_value
        if padding_width > 0:
            result_image_clipped[:, :padding_width] = border_value
            result_image_clipped[:, -padding_width:] = border_value

        return result_image_clipped

    elif border_type == cv2.BORDER_CONSTANT:
        padded_image = cv2.copyMakeBorder(
            image,
            top=padding_height, bottom=padding_height, left=padding_width, right=padding_width,
            borderType=cv2.BORDER_CONSTANT,
            value=border_value
        )
        edges = cv2.filter2D(padded_image, cv2.CV_32F, kernel, borderType=border_type)

        if center_value < 0:
            result_padded_image = padded_image.astype(np.float32) - edges
        # Na odwró†
        else:
            result_padded_image = padded_image.astype(np.float32) + edges

        result_clipped = np.clip(result_padded_image, 0, 255).astype(np.uint8)

        return result_clipped[padding_height: -padding_height, padding_width:-padding_width].copy()

    else:
        edges = cv2.filter2D(image_float, cv2.CV_32F, kernel, borderType=border_type)
        if center_value < 0:
            result_padded_image = image_float - edges
        # Na odwró†
        else:
            result_padded_image = image_float + edges
        return np.clip(result_padded_image, 0, 255).astype(np.uint8)


# Dla Lab 2 - zadanie 4
def apply_median_filter(image: np.ndarray, kernel_size: int, border_type, border_value: int):
    """
    Funkcja wykonująca operację statystyczną na obracie dla zadanej wielkości macierzy z uzupełnieniem ramek.
    :param image:
    :param kernel_size:
    :param border_type:
    :param border_value:
    :return:
    """
    padding = kernel_size // 2

    # Wypełnienie ramki konkretną wartością
    if border_type == 9999:
        result_image = cv2.medianBlur(image, kernel_size)

        # Zrobienie obramowania
        if padding > 0:
            result_image[:padding, :] = border_value    # góra
            result_image[-padding:, :] = border_value   # dół
            result_image[:, :padding] = border_value    # lewo
            result_image[:, -padding:] = border_value   # prawo

        return result_image

    # Dla BORDER_CONSTANT i BORDER_REFLECT
    else:
        # Zrobienie obramowania
        padded_image = cv2.copyMakeBorder(
            image,
            padding, padding, padding, padding,
            borderType=border_type,
            value=border_value
        )
        padded_result_image = cv2.medianBlur(padded_image, kernel_size)

        return padded_result_image[padding:-padding, padding:-padding].copy()


# Dla Lab 2 - zadanie 5
def apply_canny_edge_detection(image: np.ndarray, threshold1: int, threshold2: int):
    """
    Jak działą?

    1. Rozmywa obraz, aby nie było pojedyńczych wyróżniających się pixeli
    2. Szuka gradientów za pomocą operatora Sobela
    3. Teraz sprawdza pixele w poprzek krawędzi na gradiencie i zostawia największą wartość, a inne zeruje
    4. Progowanie dzieli na 3 obszary.
        - obszar powyżej progu górnego: na pewno to jest krawędź, zostaje taka, jaka jest
        - obszar poniżej progu dolnego: to jest szum i jest zerowany (tło)
        - obszar pomiędzy: jeżeli się styka z jakąś linnią, to jest kontynuacją linni i zostaje, a jeżeli jest
        samo sobie pozostawione to jest zerowane

    Detekcja krawędzi metodą Canny'ego
    :param image: obraz wejściowy (grayscale)
    :param threshold1: górny decyduje o tym, jakie krawędzie na pewno nimi są
    :param threshold2: wykrywa co ma nie być krawędzią w szumie
    :return: Obraz binarny z krawędziami
    """
    return cv2.Canny(image, threshold1, threshold2)