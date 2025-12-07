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
