# 1. app/io/image_io.py
## Biblioteka Path
Biblioteka tworząca obiekt ścieżki umożliwiający wykonywanie operacji na ścieżkach takich jak wyekstraktowanie samej nazwy, rozszerzenia. Te funkcje dziedziczy z klasy abstrakcyjnej PurePath.  
Biblioteka Path daje możliwość operacji Input/Output (IO) dzięki którym można zapisać, wgrać plik.

## Biblioteka NumPy
Biblioteka służąca do optymalnego i łatwiejszego operowania na listach w python.
Różnicą jest to że gdy skopiujemy tablicę numpy to jest ona kopiowana przez referencję

```
import numpy as np

a = np.ndarray([1])
b = a
b[0] = 2
print(a[0])
>> 2

```

# 2 app/model/image_store.py
Dekorator przed klasą @dataclass powoduje automatyczne utworzenie  
konstruktora klasy oraz operatorów porównywania i wyjątku w konsoli.

```
def __init__(self, params):
    ...
def __eq__(self, other):
    ...
...
```

# 3. app/model/histogram.py
## [..., 2]
Jest to wzięcie 2 elementu tablicy dla wszystkich wymiarów wyżej.

Przykład:
```
import numpy as np

myarray = np.zeros((255,255,255,), dtype=np.int64)

moje_elementy_na_drugim_miejscu_wymiar_3 = myarray[..., 1]
```