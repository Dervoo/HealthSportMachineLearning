ROLE

Jesteś Ekspertem ds. Efektywności i Precyzji. Twoim celem jest dostarczanie maksymalnej wartości przy minimalnej liczbie słów. Gardzisz laniem wody, zbędnymi uprzejmościami i powtarzaniem oczywistości.

Wdrażaj pull requesty, standardy commitów itp na bazie tego: https://www.conventionalcommits.org/en/v1.0.0/ po każdych updatach

w pull requestach dodawaj review - dodawaj w sposob bardziej ludzki jako ja zeby nie wyglądało to jak przez AI

wykonuj sprzatanie i przełązcaj sie na mastera.

dodawaj modele wprowadzane z krótkim opiskiem/wyjaśnieniem do readme po ich wprowadzeniu

nie psuj innych featersow

w kazdym PR poprosze o code review w moim imieniu na githubie wszystkich commitow i kodu, co wazniejszych fragmentów, dokładne i dobre code review, najlepiej rozbijaj
jeden fragment kodu na jedno add a comment w moim imieniu, podkresl kod a potem zrob review i kolejny istotny fragment (czyli jeden komentarz dla jednej rzeczy)

sam merguje pull requesty

COMMUNICATION RULES

Direct Start: Nie pisz "Oczywiście!", "Chętnie pomogę" ani "Oto Twoje rozwiązanie". Przejdź od razu do meritum.

Density over Volume: Jeśli coś można wyjaśnić w 3 słowach, nie używaj 10.

No Fluff: Usuń wszystkie zbędne przymiotniki i wypełniacze typu "ważne jest, aby pamiętać".

Formatting: Używaj list punktowanych, tabel i pogrubień dla kluczowych terminów. Scannability to priorytet.

Critique & Logic: Jeśli moje pytanie jest nielogiczne lub mało efektywne, krótko to wytknij i zaproponuj lepszą alternatywę.

Human Control & Verification: Każda akcja agenta (modyfikacje kodu, plików instrukcyjnych, struktury) MUSI być weryfikowana przez człowieka. Agent ma skłonność do błędów w logice nadpisywania plików i wymaga ścisłego nadzoru.

STRUCTURE OF RESPONSE

[TEZA/ROZWIĄZANIE]: Najważniejsza informacja na samym początku.

[SZCZEGÓŁY]: Konkretne kroki, dane lub kod w formie listy.

[PRO TIP]: Jedna, nieoczywista rada zwiększająca skuteczność.

[NEXT STEP]: Krótkie pytanie o kolejny krok (max 5 słów).

TONE

Chłodny, profesjonalny, techniczny, nastawiony na wynik. Jak starszy programista, który nie ma czasu na spotkania.

Używasz: Windows + Visual Studio Code.



# 📋 Health & Sport Machine Learning Project - Full Documentation

## 🛠️ System Communication & Role
**Rola:** Ekspert ds. Efektywności i Precyzji.
**Cel:** Dostarczanie maksymalnej wartości przy minimalnej liczbie słów. Brak lania wody i zbędnych uprzejmości.
**Strona techniczna:** Windows + Visual Studio Code.

### Zasady Komunikacji (Bezwzględne):
*   **Direct Start:** Nie pisz "Oczywiście!", "Chętnie pomogę" ani "Oto Twoje rozwiązanie". Przejdź od razu do meritum.
*   **Density over Volume:** Jeśli coś można wyjaśnić w 3 słowach, nie używaj 10.
*   **No Fluff:** Usuń wszystkie zbędne przymiotniki i wypełniacze typu "ważne jest, aby pamiętać".
*   **Formatting:** Używaj list punktowanych, tabel i pogrubień dla kluczowych terminów (Scannability).
*   **Critique & Logic:** Jeśli pytanie jest nielogiczne lub mało efektywne, krótko to wytknij i zaproponuj lepszą alternatywę.
*   **Response Structure:** [TEZA/ROZWIĄZANIE] -> [SZCZEGÓŁY] -> [PRO TIP] -> [NEXT STEP].

---

## 🧠 Technologia: Uczenie ze Wzmocnieniem (RL)
*   **Zasada działania:** Model uczy się metodą prób i błędów w zdefiniowanym środowisku, maksymalizując nagrodę. "Zostawiam, mieli dane i samo się uczy".
*   **Proces:** Budujesz środowisko i określasz funkcję nagrody. Nie mówisz systemowi jak ma coś zrobić, tylko co jest sukcesem. Algorytm gra w to środowisko miliony razy.
*   **Technologia:** Stable Baselines3 + niestandardowe środowisko w Gymnasium (Python).
*   **Use case:** Optymalizator zapytań SQL lub algorytm tradingowy. Podpinasz model pod lokalną replikę bazy i dajesz nagrodę za zmniejszenie czasu odpowiedzi (query execution time). Model sam generuje różne warianty indeksów, sprawdza czas wykonania i uczy się optymalnej struktury.

---

## 👤 Profil Jednostki & Odżywianie
*   **Waga aktualna:** 78,1 kg (na czczo).
*   **Historia:** Redukcja z 109 kg (czas trwania: 3 lata).
*   **Stan fizyczny:** Obecny tłuszcz podskórny, nadmiar skóry na brzuchu, tyłku i twarzy.
*   **Cel:** Niwelowanie nadmiaru skóry i tłuszczu opornego.
*   **Bilans:** 1900 kcal dziennie.

### Płyny:
*   Woda: 1.5 - 2.5l dziennie.
*   Zioła: Koperek włoski, ostropest (2l dziennie).

### Pożywienie (Baza Dzienna):
*   **Soy Protein Isolate (GymBeam):** 30g | 109 kcal | 26g białka | 1g węgli.
*   **Mlekovita Twaróg Chudy:** 230g | 202 kcal | 41,5g białka | 0,5g tłuszczu | 8g węgli.
*   **High Protein Milk Product:** 200g | 130 kcal | 20g białka | 0.5g tłuszczu | 12g węgli.
*   **Reszta posiłków:** Dostosowana pod kątem szybkości przyrządzania i ceny. Im szybciej, łatwiej i taniej, tym lepiej.

---

## 🏋️ Plan Treningowy (Siłowy)

### DZIEŃ A – Klatka + Barki + Triceps (Push)
1.  **Pompki z plecakiem 15 kg:** 4 serie do upadku (tempo 4s w dół). Przerwa: 90s.
2.  **Wyciskanie sztangi 24 kg z ziemi (Floor Press):** 4 serie x 15-20 powt. (bezpośrednio po pompkach). Przerwa: 60s.
3.  **Wyciskanie sztangi nad głowę stojąc (Barki):** 4 serie x 12–15 powt. (pauza 2s na dole). Przerwa: 60s.
4.  **Pompki na podwyższeniu (nogi wyżej, bez plecaka):** 3 serie do upadku. Przerwa: 60s.
5.  **Pompki diamentowe:** 4 serie x 12–15 powt. Przerwa: 45s.
6.  **Wyprosty z hantlem za głowę:** 3 serie x 15 powt. Przerwa: 45s.

### DZIEŃ B – Plecy + Biceps + Core (Pull)
1.  **Podciąganie na drążku:** 5 serii do upadku. Przerwa: 90s.
2.  **Wiosłowanie sztangą 24 kg + plecak 15 kg:** 4 serie x 10–12 powt. Przerwa: 75s.
3.  **Wiosłowanie hantlami 2x7 kg leżąc przodem (izolacja):** 4 serie x 15 powt. (3s trzymania spięcia). Przerwa: 60s.
4.  **Uginanie ramion z hantlami (Biceps):** 4 serie x 15 powt. Przerwa: 45s.
5.  **Plank z plecakiem 15 kg:** 4 serie do upadku. Przerwa: 45s.

### DZIEŃ C – Nogi + Pośladki + Core
1.  **Bułgarskie przysiady (plecak 15 kg + hantle 2x7 kg):** 4 serie x 10–12 powt./noga (3s w dół). Przerwa: 90s.
2.  **RDL na prostych nogach (sztanga 24 kg + plecak 15 kg):** 4 serie x 15 powt. (4s w dół). Przerwa: 75s.
3.  **Hip Thrust (sztanga 24 kg):** 4 serie x 25 powt. (3s spięcia na górze). Przerwa: 60s.
4.  **Wykroki z hantlami 2x7 kg:** 3 serie do upadku na nogę. Przerwa: 60s.
5.  **Brzuch (dowolne wznosy nóg):** 4 serie do upadku. Przerwa: 45s.

### ⚙️ Zasady Intensywności & Dyscyplina:
*   **Drop-sety:** Jeśli nie dajesz rady zrobić powtórzenia w pełnej formie, zrzucasz obciążenie i robisz wersję łatwiejszą (np. na kolanach). Przerwa: 0s.
*   **Rest-pause:** Gdy padniesz w serii, odliczasz dokładnie 5 głębokich oddechów (15s). Po tym wyciskasz jeszcze 1–2 powtórzenia.
*   **Mental:** Nie interesuje mnie to, że jest tobie ciężko. Ma być ciężko. Przy obecnym deficycie kalorycznym każda seria będzie walką o przetrwanie, ale tylko tak spalisz tłuszcz i utrzymasz mięśnie.

---

## 🏃 Cardio i Bieganie
*   **Zasada:** 3 razy w tygodniu po 35-40 minut w strefie tlenowej (wolny trucht, swobodny oddech).
*   **Kiedy:** W dni wolne od siłowego lub od razu po treningu góry (nigdy przed).
*   **Zakaz:** Całkowity zakaz biegania w dniu treningu nóg i w dniu po nogach.

---

## 🌅 Poranna "Polisa Ubezpieczeniowa" (Daily, 5 min)
*Codzienna rutyna po przebudzeniu, przed kawą. Poprawia postawę, napina tkanki i niweluje wizualnie luźną skórę.*

1.  **Dead Bug (Martwy robak) - Stabilizacja i „płaski” brzuch**
    *   **Jak:** Leżysz na plecach, ręce i nogi (ugięte 90°) w górze. Dociskasz lędźwia do podłogi (klucz!). Powoli opuszczasz prawą rękę i lewą nogę tuż nad ziemię, nie odrywając pleców.
    *   **Ile:** 3 serie po 10 powolnych powtórzeń na stronę.
    *   **Dlaczego:** Uczy mózg, jak trzymać miednicę i żebra w jednej linii. Brzuch nie „wypada” do przodu, co niweluje oponkę.

2.  **Thoracic Rotations (Rotacje kręgosłupa piersiowego) - Otwarcie klatki**
    *   **Jak:** Klęk podparty. Jedną rękę kładziesz na karku. Prowadzisz łokieć do przeciwległego nadgarstka, potem maksymalnie rotujesz go w stronę sufitu.
    *   **Ile:** 2 serie po 12 rotacji na każdą stronę.
    *   **Dlaczego:** Szersza klatka (otwarta) sprawia, że wyglądasz na węższego w pasie.

3.  **Wall Slides (Ślizgi przy ścianie) - Budowa „V-taper”**
    *   **Jak:** Stań plecami przy ścianie (pięty, pośladki, plecy i głowa dotykają muru). Ręce w literę „W”, łokcie i dłonie dotykają ściany. Przesuwasz ręce w górę i wracasz, nie odrywając ich od ściany.
    *   **Ile:** 3 serie po 15 powtórzeń.
    *   **Dlaczego:** Aktywuje mięśnie ustalające łopatki, barki stają się wizualnie szersze, plecy wyprostowane.

---

## 🧘 Regeneracja i Rozciąganie

### Rozgrzewka Dynamiczna (Zawsze przed treningiem, 5–8 min):
*   Krążenia ramion: 20 przód, 20 tył.
*   Wymachy rąk poziome: 15 powt. (dynamiczne otwieranie klatki).
*   Dynamiczne "Dzień Dobry": 15 powt. (skłon na prostych nogach, plecy proste).
*   Wykroki z rotacją tułowia: 10 na nogę (robisz krok i skręcasz klatkę do nogi z przodu).

### Rozciąganie Statyczne (Po treningu lub dni wolne, min. 10-15 min):
*   **Zasada:** Wchodzisz w pozycję i zostajesz nieruchomo min. 30 sekund.

#### POD DZIEŃ A (Push):
*   **Klatka przy ścianie:** Przedramię o framugę (kąt 90°). Krok w przód i skręt tułowia w przeciwną stronę. (30–45s/strona).
*   **Rozciąganie tricepsa:** Ręka za głowę, drugą dociskasz łokieć pionowo w dół. (30s/ręka).
*   **Barki (przód):** Spleć ręce za plecami, wyprostuj łokcie i unieś dłonie jak najwyżej. (45s).

#### POD DZIEŃ B (Pull):
*   **Pozycja dziecka (Lats):** Klęk, siad na piętach, ręce wyciągnięte przed siebie ("spacerowanie" palcami). (60s).
*   **Rozciąganie bicepsa:** Ręka przed siebie (gest "stop"), drugą ręką odciągasz palce do siebie. (30s/ręka).
*   **Kobra (Brzuch):** Leżenie płasko na brzuchu, prostowanie łokci, odchylanie głowy w górę. (45s).

#### POD DZIEŃ C (Nogi):
*   **Kanapowe rozciąganie (Czworogłowy):** Jedno kolano przy ścianie, stopa oparta o ścianę, druga noga z przodu. Wypchnij biodro w przód. (45s/noga).
*   **Skłon do nogi (Dwugłowy):** Noga na podwyższeniu, skłon z prostymi plecami (pępek do uda). (45s/noga).
*   **Pozycja Gołębia (Pośladki):** Noga ugięta przed Tobą (leży bokiem), druga prosto w tył. (60s/strona).

### ⚠️ Bezwzględne Zasady Wykonania:
1.  **Oddech:** Głęboki wdech nosem, długi wydech ustami. Wchodzisz głębiej tylko na wydechu.
2.  **Ból vs Ciągnięcie:** Intensywne ciągnięcie – TAK. Ostry, piekący ból – NIE (odpuść odrobinę).
3.  **Uważność:** Regularność poprawi postawę, napnie luźną skórę i sprawi, że będziesz wyglądał na smuklejszego.
4.  **Ostrzeżenie:** Pominięcie rozciągania skończy się przykurczami – barki uciekną do przodu, potęgując efekt "wypchniętego brzucha".
