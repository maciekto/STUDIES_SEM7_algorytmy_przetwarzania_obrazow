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


## 1. Jeżeli QPixmap jest zwracane z convert_cv_to_pixmap to nie mam potem dostępu do QImage z którego ta pixmap-a powstałą prawda?
## 2. Kiedy odznaczyłem tą linijką obraz nie zniknął self.open_windows.append(image_window) o co chodzi?