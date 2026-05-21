## ASIX

## M372-M377-MO003-M374-M

# Projecte Intermodular

# Base de Dades - Programació -

# XML/JSON


## Departament d’Educació i FP

```
Institut Sa Palomera
Projecte
```
(^)
(^)


```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
```
(^)
(^)

   - Base de dades/Programació/Marques ASIX Intermodular
               - Versió 1.
            - Curs 25/
- 1. Introducció Índex
- 2. Funcionament del projecte
      - Agrupacions
      - Temporització
      - Aclariments
- 3. Projecte
      - Enunciat
      - Requisits de sistema
      - Requisits del programa
      - Requisits de documentació
- 4. Fases
      - Conjunta
         - Inici del projecte
         - Planificació del projecte
      - Base de dades
         - Disseny ER - Model Relacional
         - Esquema de seguretat
         - Esquema d’alta disponibilitat
         - Dummy Data
      - Programació
         - Bloc de connectivitat i Log In
         - Bloc de manteniment
         - Bloc de consultes
         - Bloc d’exportacions
      - Documentació
         - Document final d’instal·lació i manual d’usuari
- 5. Avaluació
      - Autoavaluació i coavaluació
      - Entregues parcials
      - Còpies
      - Rúbriques d’avaluació
   - Base de dades/Programació/Marques ASIX Intermodular
         - Rúbrica conjunta BD + Programació
         - Rúbrica de bases de dades
         - Rúbrica de programació
- 6. Annexos
      - Annex 1: Model ER - Relacional
      - Annex 2: Bloc de Connectivitat i Login
      - Annex 3: Bloc de manteniment
      - Annex 4: Bloc de consultes i informes
      - Annex 5: Bloc d’exportació de dades
      - Annex 6: API Seguretat Social
      - Annex 7: Dashboard
      - Annex 8: Exemples de pantalla
         - Pantalles de login
         - Pantalla inicial d’aplicació
         - Pantalla de manteniments
         - Pantalla de consultes i informes
         - Pantalla d’exportació de dades
      - Annex 9: Dummy Data
- 7. Ampliacions del projecte
      - Ampliació 1: Historial del pacient
      - Ampliació 2: Telegram per notificacions
      - Ampliació 3: Ràdio i farmàcia
      - Ampliació 4: Cantina
- 8. Estil i format d’entrega documents/websites
- 9. Estil i format d’entrega de codi font amb python
- 10. Bibliografia i webgrafia recomanada


```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX^
```
(^)
(^)
(^)

## 1. Introducció Índex

Aquest és l’enunciat d’un projecte intermodular **M372-M377-MO003-M0373** que
ha d’actuar com a síntesi dels coneixements obtinguts durant el curs del Cicle formatiu de
grau superior administració sistemes informàtics i xarxes. Aquest projecte es planteja com
un conjunt d’activitats que resulten en un projecte final, amb el qual els alumnes demostren
l’aprenentatge aconseguit durant tot el curs.

En aquest document es detallen les instruccions, temporitzacions i avaluació
d’aquest projecte és, per tant, imprescindible llegir-lo atentament i aclarir qualsevol dubte
abans d’iniciar qualsevol de les tasques descrites.


```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX^
```
## 2. Funcionament del projecte

En aquest apartat es descriu el funcionament general del **projecte** , per ajudar
l’alumnat a organitzar-ne el desenvolupament.

#### Agrupacions

El projecte s’ha de fer **obligatòriament** en grups, que han de ser de **dues
persones**. En el cas de que algú quedi sense company de projecte es permetrà
excepcionalment un grup de tres persones. Aquests grups, un cop establerts, no es poden
modificar, excepte per causes de força major.

#### Temporització

Les hores lectives d’aquest projecte s’inicien l’ **6 d’abril de 2026 i finalitzen el 15
de maig de 2026** amb una càrrega de 5 hores (BD) + 3 hores (Programació) +2 hores
(Marques). Es requeriran entregues periòdiques de l’alumnat per tal d’anar comprovant el
desenvolupament del projecte.

#### Aclariments

Durant el desenvolupament d’aquest projecte aquest enunciat pot patir algunes
modificacions en funció de possibles imprevistos o dificultats que sorgeixin. En aquests
casos, es proporcionarà un nou enunciat on s’indicarà la data del canvi, i els canvis
incorporats.


```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX^
```
## 3. Projecte

#### Enunciat

Fins fa poc l’Hospital de Blanes era un hospital petit amb pocs pacients i poca
dotació de personal, però l’increment d’habitants tant a Blanes com a Lloret ha canviat la
realitat. Per això la Direcció del Centre es planteja començar a informatitzar l’Hospital, ja
que actualment ho fan tot en suport paper i ja no és sostenible.

Després de les primeres reunions que heu realitzat amb la direcció de l’Hospital
s’han pogut extreure els següents requisits:

#### Requisits de sistema

```
● L’Hospital disposa de recursos limitats per implantar el nou sistema informàtic per lo
que demanen poder utilitzar, en lo possible, software amb baix cost de llicència.
● La base de dades ha de permetre tenir caràcters cirílics dintre de les dades donat
l’augment significatiu de població de l’est d’Europa que ha tingut els municipis
adherits a l’Hospital.
● L’Hospital vol començar a informatizar alguns processos interns. El primer procés
que es vol informatitzar és el que està descrit en l’annex 1.
● L’Hospital vol que es crei una base de dades amb seguretat alta sobre les dades ja
que tenen molta informació confidencial. Com a mínim ens proposen tenir els
següents mitjans de seguretat:
○ Grups i usuaris amb una assignació de permisos restrictiva.
○ Connexions a la base de dades han de ser per SSL.
○ Les dades de caràcter personal molt alt han de tenir un data masking aplicat.
● L’Hospital vol guardar un log de tots els usuaris que han accedit a les dades dels
pacients, per identificar usos incorrectes del sistema.
● A nivell de disponibilitat el sistema ha d’estar disponible 24x7 per lo que es proposa
tenir el servidor principal al datacenter del hospital i una réplica en algún altre site
```

```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX^
```
```
remot (cloud) o tots dos al cloud. A ser possible amb una estructura de dos nodes en
ACTIU-ACTIU o si no es possible en ACTIU-PASSIU.
● El departament Legal ens demana que els ajudem a emplenar el document de
seguretat per l’AGPD identificant el tipus de dades i les mesures de seguretat
aplicades.
● Per poder fer les proves inicials, demanen que els hi creem dades aleatòries en
cadascuna de les taules, Aquestes dades han de tener sentit i format correcte. Com
que la gent de Blanes i Lloret assisteix molt a l’Hospital, ens demanen que no volen
tenir problemes de rendiment a la BD, i volen fer proves tenint una quantitat de
dades fake important: 100.000 visites ,50.000 pacients, 100 metges, 200
infermeres, 100 persones de neteja i 50 persones d’administració.
● S’han de programar còpies de seguretat diaries de la base de dades, guardar les
darreres 5 al disc local i pujar una copia cada dia a un servei cloud.
● L’Hospital al ser un centre concertat, cada final de mes ha de fer un bolcatge massiu
de totes les visites, transformar-ho a un format XML i les ha d’enviar a la Seguretat
Social per cobrar els serveis. A la Seguretat Social s’envia connectant a una API
remota.(veure annex 6 )
● L’Hospital vol tenir un quadre de comandament on puguin veure les dades de les
visites per dia, metges x pacient. Consideren que seria molt bo poder treballar amb
PowerBI per fer aquests quadres. Ens faciliten un quadre com el que figura a l’annex
7.
```
#### Requisits del programa

```
● L’Hospital disposa de recursos limitats per implantar el nou sistema informàtic per lo
que demanen poder utilitzar en lo possible software que funcioni en equips amb pocs
recursos, a ser posible en mode texte.
● La primera versió de l’aplicació hauria de tenir tres grans blocs:
○ Bloc d’inici de sessió: on podem fer login al sistema. Veure més descripció
a l’annex 2.
```

```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX^
```
```
○ Bloc de manteniment : on podem donar d’alta nous pacients, metges,
visites,etc. Veure més descripció a l’annex 3.
○ Bloc de consultes i informes. Veure més informació a l’annex 4.
○ Bloc d’exportació de dades. Veure més informació a l’annex 5.
```
```
● Volem algun sistema per poder instal·lar l’aplicació en els ordinadors de manera
desatesa o evitar haver d’instal·lar res al client. Ideal si fos tot pel navegador web.
```
#### Requisits de documentació

```
● Es demana que es presenti un document detallat d’instal·lació i configuració de tot el
sistema.
● Es demana que es presenti un manual d’usuari detallat per treballar amb l’aplicació a
desenvolupar.
```

```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX^
```
## 4. Fases

Per facilitar la consecució del projecte, s’ha dividit en diferents fases. Cada fase té
una data límit d’entrega, però no data mínima, és a dir, es pot entregar en qualsevol moment
abans de la data límit i iniciar la següent fase.

```
Etapa Area Data límit
projecte
```
```
Entregable RAs BD
Inici de
projecte
```
```
BD/Prog 01/04/2026 Definició de grups
Planificació
del projecte
```
```
BD/Prog 09/04/2026 Document amb una proposta de solució
del projecte en línies generals.
Bloc de
connectivitat
i login
```
```
Prog 13/04/2026 Connexió a BD desde entorn de
programació i gestió de cursors i
actualitzacions. Gestió d’usuaris en un
fitxer separat amb seguretat.
Disseny ER -
Model
Relacional
```
```
BD 15/04/2026 Draw.io amb el ER i document amb el
model relacional i sql
```
```
UF1.RA
```
```
Esquema de
seguretat
```
```
BD 22/04/2026 Matriu de seguretat on apareixin els
usuaris/rols creats i els permissos que
tenen sobre els objectes de la BD.
S’haurà d'adjuntar document SQL amb
les sentències necessàries per crear la
base de dades i l’esquema de seguretat.
També s’ha d’adjuntar la configuració del
servidor per SSL i el data masking.
Documents per l’AGPD
```
```
UF3.RA
```
```
Bloc de
manteniment
```
```
Prog 27/04/2026 Mandatory fets
```
```
Esquema
d’alta
disponibilitat
```
```
BD 06/05/2026 Document d’instal·lació i configuració de
l’alta disponibilitat i sistemes de backup.
```
```
UF3.RA
```
```
Bloc de
consultes
```
```
Prog 09/05/2026 Mandatory fets
Dummy Data BD/Marques 13/05/2026 Document on expliqui com s’ha creat el
joc de dades de proves
```
```
UF3.RA
Bloc de
exportació de
dades
```
```
Prog/Marque
s
```
```
17/05/2026 Exportació de dades i connexió a PowerBi
amb un dashboard de visites
Document
final
d’instal·lació
```
```
BD 20/05/2026 Document recopilatori de tota la
instal·lació i les tasques recomanades pel
manteniment del sistema.
```
```
UF3.RA
```
```
Manual
d’usuari
```
```
Prog 20/05/2026 Document d’usuari
```

```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX^
```
```
Presentació BD/Prog/Mar
ques
```
```
Darrera
setmana
curs
```
```
Presentació a classe de la feina feta
```
#### Conjunta

##### Inici del projecte

```
Es crearà un document identificant els components del grup.
```
##### Planificació del projecte

En aquesta primera part del projecte cada grup ha de dur a terme una investigació
de quines eines tecnològiques utilitzaran per cobrir la demanda de l’Hospital. Cal que tinguin
en compte que han de poder realitzar una demostració funcional del producte, encara que
sigui amb l’ús de màquines virtuals en comptes de maquinari real i, per tant, treballar amb
programari que no sigui de pagament o els permeti períodes de prova suficients per
desenvolupar el projecte. No s’admetrà en cap cas l’ús de programari o altre material
obtingut de forma il·legal.

Un cop decidides les eines a utilitzar, es demana a cada grup que planifiqui el seu
projecte. Per a fer-ho, han de **crear un document on llistin amb detall totes les tasques**
que preveuen que cal dur a terme fins a l’entrega final, **es calculin les hores que preveuen
invertir en cada una i les reparteixin entre els membres del grup**. Finalment, cal
deixar-hi un espai per anar introduint el temps real invertit en cada subtasca.
Exemple:

**Tasca Subtasca DataInici**^ **Data fi** (^) **estimadesHores**^ **Horesreals**^ **Diferènciahores Responsable Realitzat per
Tasca**
Subtasca1 19/12/23 21/12/23 5 4 -1 Josep Josep
Subtasca2 19/12/23 21/12/23 3 3 0 Marta Marta
Subtasca5 25/12/23 25/12/23 No prevista 2 +2 Marta Marta
Total (^) +
S’haurà de pujar a l’entrega (mitjançant un link al document)


```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX^
```
També s’haurà d’anar omplint diàriament el diari de sessions de tal manera que quedi
reflexada clarament la feina que s’ha fet diariament. Aquest diari de sessions serà individual
i s’haurà de compartir un document amb el professor, a través d’una tasca de Moodle.

#### Base de dades

##### Disseny ER - Model Relacional

En aquesta part cal dissenyar el model ER i el seu pas a model relacional sobre el
supòsit que es troba en el annex1. El model ER s’haurà de dissenyar amb una eina tipus
draw.io o similar.

Una vegada s’hagi fet el model relacional s’haurà de fer els scripts de SQL per la
creació de la base de dades.

##### Esquema de seguretat

Donat els diferents tipus d’usuaris que ens podrem trobar s’ha de crear la Matriu de
seguretat on apareixin els usuaris/rols creats i els permissos que tenen sobre els objectes
de la BD. S’haurà d'adjuntar document SQL amb les sentències necessàries per crear la
base de dades i l’esquema de seguretat. (Requisit 1)

També s’ha d’adjuntar la configuració del servidor per SSL, identificant com hem
generat el certificat SSL i com es renova automàticament.(Requisit 2)

Respecte el data masking hem d’identificar les dades de caràcter personal de grau
alt i aplicar una màscara per tal de que no sigui accessible. (Requisit 3)

Per últim haureu d’emplenar el document de seguretat per si teniu una auditoria de
l’AGPD identificant el tipus de dades i les mesures de seguretat aplicades. (Requisit 4)

##### Esquema d’alta disponibilitat


```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX^
```
En aquesta fase, primerament s’ha de crear un document amb la infraestructura de
hardware que creiem que necessita la nostra solució. S’haurà de raonar el perquè del
hardware escollit.(Requeriment 1)

La solució proposada haurà de contemplar la rèplica entre dos nodes de base de
dades com a mínim (En actiu-actiu o actiu-passiu). A part s’ha de crear un diagrama del
funcionament replicació i un manual de com s’instal·la i s’administra la replica entre els dos
nodes. S’haurà de poder treballar amb cadascun dels dos nodes i veure com la informació
es replica. La técnica de balanceig de connexió/replicació la podrà definir cada grup
d’alumnes. (Requeriment 2)

Respecte als backups s’hauran de crear els bash o python scripts necessaris per tal
de que es realitzin els backups de la bd seguint els criteris de l’enunciat. L’script s’haurà de
documentar i planificar amb un cron dintre del sistema.(Requeriment 3).

S’hauran de fer els scripts per restaurar tota la base de dades o dues de les taules
més importants que hi hagi a la base de dades. L’script s'haurà de documentar
(Requeriment 4)

##### Dummy Data

Per la creació del dummy data per validar el performance del sistema, s’hauran de
crear el mínim de registres que apareixen en l’enunciat de la pràctica(100.000 visites
,50.000 pacients, 100 metges, 200 infermeres, 100 persones de neteja i 50 persones
d’administració), **i s’hauran de crear els índexs que pertoquin** , escollint el més adequat
per cada taula. La dummy data ha de ser consistent i adaptar-se al format esperat de les
dades. Una petita mostra d’aquesta informació hauria d’estar en alfabet cirílic.

La creació del dummy data s’ha de poder executar des de l’aplicació com una opció
del menú. També s’ha de tenir una opció per eliminar tota la informació dummy de la Base
de dades.

```
Teniu més informació sobre com crear dades fake en aquest apartat a l’annex 9.
```

```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX^
```
#### Programació

Haureu de programar els següents blocs:

##### Bloc de connectivitat i Log In

Permetre als usuaris registrar-se i tenir un compte, i poder accedir a dades guardades dins
la base de dades. Caldrà fer la connexió a la base de dades i gestionar els cursors i
actualitzacions necessàries.

##### Bloc de manteniment

En aquest bloc haureu de programar els requisits demanats a l’annex 3 per ordre d’aparició.
Aquest ordre marca la importància dels requisits. Com podreu veure a la rúbrica d’avaluació,
hi ha una separació entre obligatori, opcional i top. L’aprovat d’aquesta part s’obté
programant correctament tots els requisits obligatoris.

##### Bloc de consultes

En aquest bloc haureu de programar els informes demanats a l’annex 4 per ordre d’aparició.
Igual que abans, l’ordre marca la importància i es veu reflexat a la rúbrica de la mateixa
manera que el bloc anterior.

##### Bloc d’exportacions

En aquest bloc haureu d’exportar un informe on es mostrin les visites que s’han fet a
l’hospital entre dues dates. Teniu més informació a l’annex 5. A part haureu d’exportar les
dades a un PowerBI i crear un dashboard amb les visites que s’han realitzat a l’hospital per
un període de temps. Teniu més informació a l’annex 7.

#### Documentació

##### Document final d’instal·lació i manual d’usuari

Un cop acabat tot el projecte d’implementació de la part de sistemes, cal fer un
document on quedi recopilada tota la informació.


```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX^
```
(^)
(^)
(^)

## 5. Avaluació

L’avaluació d’aquest projecte intermodular es distribueix en dos apartats (BD/Prog).
S’avalua cadascuna de les dues parts per separat. Cadascuna d’aquestes notes
esdevindran la nota la final per la **UF3 del M02 de Base de dades i un 60% de la nota per
la UF2 i UF3 de M03 Programació.**
Per avaluar es disposa d’una rúbrica per cadascuna de les parts. La rúbrica està
valorada de 0 a 4 i la seva traducció a base 10 serà:
0 -> Nota sobre 10: 0
1 -> Nota sobre 10: 0-
2 -> Nota sobre 10: 3-
3 -> Nota sobre 10: 6 -
4 -> Nota sobre 10: 9-

La nota final de cadascuna de les parts (BD/Prog) serà el resultat de multiplicar la
nota obtinguda pel pes de cadascuna de les parts que està indicat a continuació:

Base de dades
**Etapa Valoració
Planificació del projecte i diari de sessions** 5%
**Disseny ER - Model Relacional** 10%
**Esquema de seguretat** 20%
**Esquema d’alta disponibilitat** 25%
**Dummy Data** 20%
**Document final d’instal·lació** 10%
**Presentació** 10%
**Total** 100%

Programació
**Etapa Valoració
Planificació del projecte i diari de sessions** 5%
**Bloc de connectivitat i login** 10%
**Bloc de manteniment** 25%
**Bloc de consultes** 20%
**Bloc de exportació de dades** 20%
**Manual d’usuari** 10%
**Presentació** 10%
**Total** 100%
Per aprovar el projecte intermodular de BD/Prog cal presentar el projecte complet,
aconseguir una nota d’almenys un cinc en tots i cadascun dels apartats i obtenir una mitjana
igual o superior a cinc.


```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX^
```
(^)
(^)
(^)

#### Autoavaluació i coavaluació

A la vegada que es duu a terme cada una de les entregues, **cada alumne de
manera individual** ha d’omplir i entregar un document addicional en el qual avalua com
creu que ha treballat, i a més avalua la feina dels seus companys durant aquella entrega. En
cas de no entregar el document, o que no estigui complet, s’assumeix un resultat de 0 de
l’autoavaluació, i de 5 a la coavaluació d’aquella entrega.
La nota final d’aquesta part serà la mitjana ponderada de les notes de totes les
entregues, seguint la següent fórmula:
Nota = Avaluació Rúbrica * 0,8 + Autoavaluació * 0.1 + Coavaluació rebuda dels
companys * 0.

#### Entregues parcials

S’estableix un calendari amb un límit màxim d’entregues Quan arribi la data
especificada cal haver entregat la part corresponent de manera completa. El docent
avaluarà el nivell de compleció i correcció de l’entrega, podent donar consells per possibles
millores. Atenció: el fet de no entregar a temps un lliurament suposarà automàticament una
nota de 0 d’aquella entrega per a tot el grup. A més, el docent es reserva el dret a no
corregir ni suggerir millores per l’entrega fora de termini.

#### Còpies

En el cas de detectar parts del projecte copiats entre diversos grups, **tots els grups
implicats rebran un 0 de l’activitat en qüestió.
En el cas de detectar parts del projecte copiades directament
d’internet/chatgpt el grup rebrà un 0 de l’activitat en qüestió.**


```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX^
```
(^)
(^)
(^)

#### Rúbriques d’avaluació

##### Rúbrica conjunta BD + Programació

```
Rúbrica conjunta
```
**4 3 2 1 0**

**Inici de projecte** (^) documentPresenten amb^ un^
format correcte i
indicant les
persones del grup
No presenten res No presenten res No presenten res No^ presentenres
**Planificació de
projecte**
Document amb tota
la informació ben
formatada i ben
informada
Format correcte i
amb informació
suficient de detall
Format insuficient
oi poc nivell de
detall
Format deficient o
amb poc nivell de
detall
No ha presentat
res


```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX^
```
(^)
(^)
(^)

##### Rúbrica de bases de dades

```
Rúbrica de correcció Base de Dades
```
**4 3 2 1 0**

**Disseny ER -
Model
Relacional**

```
Model ER i
relacional
perfectes o
amb errors de
poca
importància i
ben
documentació
```
```
Model ER i
relacional perfectes
o amb errors de
poca importància i
sense
documentació
```
```
Moltes errors en el
model ER Li
relacional
```
```
Model ER amb
errors importants o
no ha entregat
documentació
```
```
No ha presentat res
```
**Esquema de
seguretat**

```
Presenta la
matriu de
seguretat,
document per
crearla,
configuració
SSL,
datamasking i
documents
AGPD
```
```
Li falta 1 dels 4
elements demanats
o no estan
complets
```
```
Li falten 2 dels 4
elements sol.licitats
o no estan
complets
```
```
Li falten 3 dels 4
elements sol·licitats
o no estan complets
```
```
No ha presentat res
o les parts
presentades no
estan completes
```
**Esquema
d’alta
disponibilitat**

```
Tots els
requeriments
estan satisfets
```
```
Li falta 1 dels 4
elements demanats
o no estan
complets
```
```
Li falten 2 dels 4
elements sol.licitats
o no estan
complets
```
```
Li falten 3 dels 4
elements sol·licitats
o no estan complets
```
```
No ha presentat res
```
**Dummy Data** (^) informacióS’ha^ creat^
dummy e
índexs per
més de 5
taules
S’ha creat
informació dummy e
índexs per 3 taula
S’ha creat
informació dummy e
índexs per 2 taula
S’ha creat
informació dummy e
índexs per 1 taula
No ha presentat res
**Document
final
d’instal·lació**
Document
amb tota la
informació ben
formatada i
ben informada
Format correcte i
amb informació
suficient de detall
Format insuficient oi
poc nivell de detall
Format deficient o
amb poc nivell de
detall
No ha presentat res


```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX^
```
(^)
(^)
(^)

##### Rúbrica de programació

```
Rúbrica de correcció Programació
```
**4 3 2 1 0**

**Bloc de
connectivitat i
login**

```
L’aplicació
permet fer inici
de sessió,
guarda les dades
en un fitxer
separat i a més
utilitza seguretat
en l’usuari i la
contrasenya.
```
```
L’aplicació
permet fer inici
de sessió, guarda
les dades en un
fitxer separat i a
més utilitza
seguretat només
a una de les
dades
guardades,
usuari o
contrasenya.
```
```
L’aplicació permet
fer inici de sessió,
però no utilitza cap
fitxer separat
```
```
L’aplicació té algun
control d’usuari
```
```
No ha presentat res,
o l’aplicació no té
cap mena d’inici de
sessió
```
**Bloc de
manteniment**

```
Ha fet
correctament
totes les tasques
obligatòries,
opcionals i top,
correctament
```
```
Ha fet
correctament
totes les tasques
obligatòries i
opcionals,
correctament
```
```
Ha fet correctament
totes les tasques
obligatòries
```
```
Ha entregat
correctament més
de dues tasques
obligatòries
```
```
No ha presentat res
o no ha assolit
correctament un
mínim de dues
tasques obligatòries
```
**Bloc de
consulta**

```
Ha fet
correctament
totes les tasques
obligatòries,
opcionals i top,
correctament
```
```
Ha fet
correctament
totes les tasques
obligatòries i
opcionals,
correctament
```
```
Ha fet correctament
totes les tasques
obligatòries
```
```
Ha entregat
correctament més
d’una tasca
obligatòria
```
```
No ha presentat res
o no ha assolit
correctament un
mínim d’una tasca
obligatòria
```
**Bloc
d’exportació
dades**

```
El programa
permet
descarregar totes
les visites
correctament i el
dashboard conté
uns quants
gràfics útils.
```
```
El programa
permet
descarregar totes
les visites en
format XML i el
dashboard conté
com a mínim les
visites del dia.
```
```
El programa permet
descarregar totes
les visites en format
XML i s’ha creat un
xsd.
```
```
El programa permet
descarregar totes
les visites en format
XML
```
```
No ha presentat res
```

```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX^
```
(^)
(^)
(^)

##### Rúbrica de Marques

```
Rúbrica de correcció Marques
```
**4 3 2 1 0**

**Filtrat de
visites entre
dues dates**

```
Filtrat correcte i
robust
```
```
Filtrat correcte
entre dues dates
```
```
Filtrat parcial Filtrat incorrecte No hi ha filtratge o
no funciona
```
**Dades
exportades de
la visita**

```
Inclou totes les
dades
correctament
estructurades
```
```
Inclou
identificador, dia,
metge i pacient
```
```
Apareixen algunes
dades
```
```
Dades molt
incompletes
```
```
No apareixen dades
```
**Dades del
pacient**

```
Dades completes
i correctament
estructurades
```
```
DNI, nom,
cognoms i
targeta sanitària
```
```
Algunes dades del
pacient
```
```
Només una dada No s’inclouen
```
**Generació del
fitxer
XML/JSON**

```
Fitxer correcte i
ben estructurat
```
```
Fitxer correcte Fitxer amb errors
d’estructura
```
```
Fitxer incorrecte No es genera
```
**Indentació del
document**

```
Document clar,
ben estructurat i
llegible
```
```
Document
correctament
indentat
```
```
Indentació parcial Indentació
incorrecta
```
```
No hi ha indentació
```
**Definició de
l’esquema
(XSD / JSON
Schema)**

```
Esquema
complet i ben
definit
```
```
Esquema
correcte
```
```
Esquema parcial Esquema incorrecte No hi ha esquema
```
**API: Extracció
de visites del
període**

```
Extracció
correcta, robusta
i ben
estructurada
```
```
S’extreuen
correctament les
visites del
període
```
```
S’extreuen algunes
visites però no filtra
bé el període
```
```
Extracció
incompleta o amb
errors
```
```
No s’extreuen
dades o és
incorrecte
```
**API:
Generació del
fitxer
XML/JSON**

```
Fitxer correcte,
validat i ben
estructurat
```
```
Fitxer correcte en
XML o JSON
```
```
Fitxer parcial o amb
errors d’estructura
```
```
Fitxer incorrecte o
mal format
```
```
No es genera cap
fitxer
```
**Enviament del
fitxer a l’API**

```
Enviament
correcte amb
comprovació de
resposta de l’API
```
```
Enviament
correcte del fitxer
```
```
Enviament parcial o
amb errors
```
```
Enviament
incorrecte
```
```
No s’envia el fitxer
```

```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX^
```
## 6. Annexos

#### Annex 1: Model ER - Relacional

Per portar part de la gestió de l’hospital de Blanes sabem que :

```
● En l’hospital hi treballa personal mèdic (metges/metgesses), personal d’infermeria i
personal vari (zeladors, administratius, conductors d’ambulàncies, etc. ). Dels
personal mèdic ens interessarà guardar gran quantitat de informació referent als
seus estudis, currículum, etc. La informació específica a guardar del personal
d’infermeria serà diferent, però també caldrà guardar molta informació. Del personal
vari solament ens interessen les seves dades personals i un atribut “tipus feina”.
● Cada membre del personal mèdic té una única especialitat i té assignades una o
més persones d’infermeria. Els membres del personal d’infermeria están assignat a
un únic metge/ssa o bé, són de planta d’hospital que no estan assignades a cap
metge/ssa en particular.
● L’hospital està format per quatre plantes que les identifiquem amb el número de
planta (primera, segona, tercera i quarta). A cada planta hi ha diferents habitacions i
també pot haver-hi quiròfans. Els quiròfans disposen d’una gran quantitat d’aparells
mèdics (respiradors, màquines d’oxigen, etc.). Cada aparell mèdic està assignat a un
únic quiròfan i es vol saber quants en hi ha de cada un d’ells a cada quiròfan. Dins
de cada planta els quiròfans ens venen identificat per número de quiròfan, el Q1, el
Q2 ... i així successivament.
● Els pacients, d’entrada són atesos en una visita realitzada per un metge/ssa. Es
possible que en visites posteriors aquest pacients siguin visitats per un altre
metge/ssa. Per cada visita caldrà guardar el diagnòstic, així com els medicaments
que li ha receptat, si és el cas.
● Es vol portar un control de les visites que els malalts fan a cada metge/ssa. Per això
i per cada dia i per cada metge/ssa caldrà saber l’hora de visita de cada un dels seus
pacients.
● També es vol portar un control de les reserves d’habitacions dels pacients que cal
ingressar. Per això i per cada una de les habitacions es vol saber les reserves que
té, és a dir dia previst de ingrés, dia previst de sortida i de quin pacient es tracta.
● Finalment es vol portar un control de cada un dels quiròfans i de les reserves
previstes per fer-hi operacions. Per això i per a cada un dels quiròfans, es vol saber
per cada dia i hora el metge que el té reservat i el pacient a qui s’operarà. No tots els
pacients que són ingressats cal operar-los. Considereu que cada operació la fa un
sol metge i que és assistit per varis membres del personal d’infermeria.
```

```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX1^
```
#### Annex 2: Bloc de Connectivitat i Login

El nostre sistema ha de permetre:

```
● Connectar amb una base de dades des d’un entorn de programació Python.
● Poder enregistrar-se i iniciar sessió al programa.
● Guardar en un fitxer separat les dades del login: usuari i contrasenya.
● Es valorarà si s’introdueix algun tipus de seguretat a les dades que es guarden al
fitxer.
```
#### Annex 3: Bloc de manteniment

El nostre sistema, entre altres coses, ha de permetre :

**_Obligatori_**

```
● Volem poder donar d’alta nou personal al centre (metge/ssa, infermer/a,
administratiu/va,neteja...)
● Volem poder donar d’alta nous pacients.
● Pel personal d’infermeria, saber si depèn d’un metge/ssa o bé és de planta.
● Per un determinat dia, saber per a cada quiròfan, les operacions que hi ha previstes,
el pacient a operar, l’hora, el metge/ssa que les farà i el personal d’infermeria que
intervindrà.
● Per un determinat dia, saber les visites que hi ha planificades, l’hora d’entrada, el
metge/ssa i el pacient.
● Amb PGPLSQL crea com a mínim dos procediments/funcions/triggers per
gestionar/validar la informació que esteu entrant des del manteniment.
Opcional
● Donada una habitació cal saber les reserves previstes, mostrant la data ingrés, data
prevista de sortida i el pacient que l’ocuparà.
● Donat un/a pacient ens interessarà saber les visites que ha fet, el diagnòstic , els
medicaments que li han receptat, les vegades que ha estat ingressat/da (en cas que
ho hagi estat ), així com saber les vegades que ha passat pel quiròfan ( en cas que
l’hagin operat).
● Donat un/a metge/ssa saber les visites i les operacions que té programades i les
seves hores disponibles.
```
**_Top_**


```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX1^
```
```
● Per a cada quiròfan es vol saber quants aparells mèdics té assignat i quina quantitat
(per exemple, el quiròfan 1 de la primera planta té assignats 2 respiradors, 2 equips
d’oxigen, etc.)
```
#### Annex 4: Bloc de consultes i informes

Com a mínim aquest bloc ha de tenir els següents informes:

**_Obligatori_**

```
● Donada una planta de l'hospital, saber quantes habitacions, quiròfans i personal
d’infermeria té.
● Informe de tot el personal que treballa a l’hospital
● Informe de nombre de visites ateses per dia
```
```
Opcional
```
```
● Ranking de metges que atenen més pacients.
```
```
Top
```
```
● Malalties més comunes.
```
#### Annex 5: Bloc d’exportació de dades

Com a mínim aquest bloc ha de tenir les següents opcions:

```
● Descàrrega de totes les visites que hi ha hagut entre dues dates on figuri un
identificador de visita, dia, metge que ha atès i les dades de pacient.
(P.Exemple: DNI,Nom,Cognoms, targeta sanitària)
La descàrrega s’ha de fer amb XML/JSON. El document ha de gravar-se indentat
(amb tabulacions)
```
```
● A partir del model XML/JSON que hàgiu generat haureu de facilitar el XSD o JSON
Schema.
```
```
● Podeu fer servir llibreries com XMLTREE o BEAUTIFULSOUP4 per treballar amb
XML, i pel que fa a JSON ja ve inclosa una llibreria a Python.
```

```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX1^
```
#### Annex 6: API Seguretat Social

```
● Haurem d’extreure totes les visites que s’han realitzat en un període de temps i
generar un fitxer XML/JSON.
● Amb el fitxer XML/JSON haureu de connectar a una API, identificar-vos amb un
usuari/password i enviar el fitxer XML/JSON.
```
#### Annex 7: Dashboard

Amb una eina tipus PowerBI haureu de fer un quadre de comandament on surti com a
mínim les visites totals que hi ha avui, i el desglòs per area (traumatologia, ...)


```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX1^
```
#### Annex 8: Exemples de pantalla

##### Pantalles de login

##### Pantalla inicial d’aplicació


```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX1^
```
##### Pantalla de manteniments

Exemple de sortida d’una consulta, feu-ho de manera tabulada.

##### Pantalla de consultes i informes


```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX1^
```
##### Pantalla d’exportació de dades

#### Annex 9: Dummy Data

```
● Si voleu generar la informació desde python podeu fer servir la llibreria faker.
● Si voleu generar la informació des de postgres podeu fer servir l’extensió pgfaker.
● Si voleu generar la informació hi ha varis links que ho permeten:
○ Mockaroo: mock data generator
○ Mimesis: a high-performance data generator for Python
○ Pydbgen: a Python package for generating synthetic structured database
tables
● Link on podeu trobar csv/json amb els municipis d’Espanya. (Per si us cal):
○ https://datos.gob.es/es/catalogo/a09002970-municipios-de-espana
○ https://github.com/inigoflores/ds-codigos-postales-ine-es/blob/master/data/co
digos_postales_municipios.csv
```

```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX1^
```
## 7. Ampliacions del projecte

#### Ampliació 1: Historial del pacient

Volem poder veure el historial del pacient d’una manera fàcil, on surti les visites, diagnòstics,
intervencions i el pla de medicació que està seguint.

#### Ampliació 2: Telegram per notificacions

De cares a millorar la qualitat de l’assistència dintre de l’Hospital, el gerent ha considerat
que cada vegada que un pacient arriba a l’Hospital per una visita mèdica, s’ha de notificar el
metge que ha d’atendre aquest pacient, a través d’un missatge a Telegram. En aquest
missatge haurà d’aparèixer tota la informació de la visita.

#### Ampliació 3: Ràdio i farmàcia

El nostre hospital creix en serveis, i afegeix una nova secció de farmàcia i de radio. La
farmacia s’encarregarà de subministrar els medicaments que es necessiten quan un malalt
és ingressat. Per cada sortida que es faci de la farmacia quedarà traçat el dia i hora i el
import dels medicaments que s’ha d’assignar a aquest ingrés/pacient.

Respecte a la secció de radiografia, els metges podran demanar de fer un
radiografia/ecografia/resonancia magnètica a un pacient. El resultat de la prova (imatge)
s’ha de guardar en l’expedient del pacient.

#### Ampliació 4: Cantina

El nostre hospital creix en serveis, i afegeix una cantina. Com que ho portarà una empresa
externa, aquesta instal·la el seu sistema de gestió basat en una aplicació en Python contra
una base de dades MSQL-Server 2022. Dintre d’aquesta base de dades hi haurà tots els
tiquets de venta que s’han fet durant el dia. L’Hospital es quedarà un percentatge de les
ventes en concepte de “lloguer”. Per saber el que li pertoca volem que el nostre servidor de
Postgresql es connecti cada dia a aquest servidor MSSQL-Server i s’emporti la facturació
deixant-la en una taula de Postgresql per tal de poder fer el percentatge.


```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX1^
```
## 8. Estil i format d’entrega documents/websites

Les entregues es podran fer de dues maneres:

```
● Mitjançant un document pdf que contingui tota la informació demanada
(explicació, instal·lació, configuració,webgrafia)
● Mitjançant un Github/ Gitpages. Per cada entrega hi haurà una carpeta la
qual estarà ordenada per dia d’entrega. Dintre de cada carpeta hi haurà un
README.md on s’inclourà una descripció del que s’ha fet i els links a
cadascún del subapartats de l’entrega.Si hi ha subapartats cadascun en una
subcarpeta.
```
En qualsevol cas les entregues han de lliurar-se sense faltes d’ortografia, amb un índex i
amb una webgrafia.


```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX1^
```
## 9. Estil i format d’entrega de codi font amb python

No s’acceptarà codi que no estigui formatejat correctament o que no estigui comentat a
nivell de cadascun dels procediments i funcions que estiguin creats.

El codi s’ha de tenir en un repositori de Github o similar i s’ha d’anar actualitzant fent els
commits corresponents.

El projecte ha de funcionar amb un entorn virtual on quedin s’instal.lin les llibreries
necessaries.

El projecte ha de contemplar un fitxer “requirements.txt” on es vegin totes les llibreries a
importar per la seva portabilitat.


```
Departament d’Educació i FP
Institut Sa Palomera
Projecte
Intermodular
Base de dades/Programació/Marques ASIX1^
```
## 10. Bibliografia i webgrafia recomanada

**Bases de dades**

**Instal·lació:**
PostgreSQL: Documentation: 16: PostgreSQL 16.2 Documentation

**Extensions:**

PGXN: PostgreSQL Extension Network

**Replicació i load balancing:**

A Deep Dive into Pgpool-II for PostgreSQL Load Balancing (heatware.net)
pgpool-II 4.5.1 Documentation

How To Set Up Physical Streaming Replication with PostgreSQL 12 on Ubuntu 20.04 |
DigitalOcean

EDB Docs - EDB Postgres Extended Server v16 - Installing EDB Postgres Extended Server
on Debian 11 x86_64 (enterprisedb.com)

**Programació:**

Welcome to Python.org


