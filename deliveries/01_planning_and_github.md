# 1. Planificació del Projecte i GitHub

## Grup

| Membre         | Rol                     |
| -------------- | ----------------------- |
| Yossef Errazik | Desenvolupament complet |

## Enllaç al repositori

**GitHub:** https://github.com/yosseferrazik/hospital-management-project

El projecte es desenvolupa a la branca `main` amb commits directes. S'ha seguit un enfocament de desenvolupament continu, on cada funcionalitat es va incorporant progressivament al codi principal.

## Tecnologies escollides

| Capa           | Tecnologia              | Per què                                           |
| -------------- | ----------------------- | ------------------------------------------------- |
| Backend        | Python 3.12 + Flask 3.1 | Ja el coneixíem de classe, zero cost de llicència |
| Base de dades  | PostgreSQL 16           | Complir requisits (ciríl·lic, SSL, replicació)    |
| ORM            | SQLAlchemy 2.0          | Prevenir SQL injection, facilitar manteniment     |
| Client         | Tkinter                 | Va inclòs amb Python, funciona en equips modestos |
| Dashboard      | Chart.js                | Alternativa gratuïta a PowerBI                    |
| Autenticació   | JWT + bcrypt            | Estàteless, suficient per a ús intern             |
| Virtualització | Tailscale               | Connectar els dos nodes sense obrir ports públics |

## Planificació de tasques

| Tasca                           | Subtasca                                            | Data inici | Data fi    | Hores est. | Hores reals | Desviació | Responsable |
| ------------------------------- | --------------------------------------------------- | ---------- | ---------- | ---------- | ----------- | --------- | ----------- |
| **Planificació**                | Definir grups, eines i planificació                 | 01/04/2026 | 09/04/2026 | 4          | 5           | +1h       | Yossef      |
| **Connectivitat i login**       | Connexió BD, registre, login, fitxer de credencials | 06/04/2026 | 13/04/2026 | 6          | 7           | +1h       | Yossef      |
| **ER - Model Relacional**       | Diagrama ER, model relacional, SQL                  | 06/04/2026 | 15/04/2026 | 5          | 6           | +1h       | Yossef      |
| **Esquema de seguretat**        | Rols, RLS, SSL, data masking, AGPD                  | 15/04/2026 | 22/04/2026 | 8          | 9           | +1h       | Yossef      |
| **Bloc de manteniment**         | CRUD personal, pacients, visites, cirurgies         | 13/04/2026 | 27/04/2026 | 10         | 12          | +2h       | Yossef      |
| **Alta disponibilitat**         | Replicació, backups, restore, monitorització        | 22/04/2026 | 06/05/2026 | 10         | 14          | +4h       | Yossef      |
| **Bloc de consultes**           | Informes i reports                                  | 27/04/2026 | 09/05/2026 | 8          | 8           | 0h        | Yossef      |
| **Dummy Data**                  | Generació de dades falses, càrrega massiva          | 06/05/2026 | 13/05/2026 | 6          | 7           | +1h       | Yossef      |
| **Exportació de dades**         | XML/JSON, XSD, API Seguretat Social, Dashboard      | 09/05/2026 | 17/05/2026 | 8          | 10          | +2h       | Yossef      |
| **Document final instal·lació** | Guia d'instal·lació completa                        | 13/05/2026 | 20/05/2026 | 4          | 5           | +1h       | Yossef      |
| **Manual d'usuari**             | Guia d'ús de l'aplicació                            | 13/05/2026 | 20/05/2026 | 4          | 4           | 0h        | Yossef      |
| **Document final**              | Recopilatori de tot el projecte                     | 17/05/2026 | 20/05/2026 | 4          | 4           | 0h        | Yossef      |

## Diagrama de Gantt (seqüenciació temporal)

```
Abril 2026                              Maig 2026
Set 1  Set 2  Set 3  Set 4  Set 1  Set 2  Set 3
[Planificació]
[Connectivitat] [########]
[ER Model]      [############]
                [Seguretat]   [########]
                [Manteniment] [############]
                              [Alta Disp.] [##############]
                              [Consultes]   [############]
                                            [Dummy Data] [######]
                                            [Exportació] [##########]
                                                          [Doc Instal] [#####]
                                                          [Manual Us]  [#####]
                                                          [Doc Final]  [####]
```

## Gestió de branques i commits

### Estratègia de branques

Tot i que el projecte s'ha desenvolupat principalment a la branca `main` (tractant-se d'un projecte individual), s'ha seguit una disciplina de commits atòmics amb missatges descriptius seguint la convenció **Conventional Commits**:

| Tipus de commit | Ús                                              | Exemple                                                    |
| --------------- | ----------------------------------------------- | ---------------------------------------------------------- |
| `feat:`         | Nova funcionalitat                              | `feat: add JWT authentication endpoint`                    |
| `fix:`          | Correcció d'error                               | `fix: handle null staff_id in token decoder`               |
| `docs:`         | Documentació                                    | `docs: add AGPD compliance report`                         |
| `refactor:`     | Canvi intern sense canvi de comportament        | `refactor: extract db session to context manager`          |
| `test:`         | Afegir o modificar tests                        | `test: add unit tests for login edge cases`                |
| `chore:`        | Tasques de manteniment (deps, config, scripts)  | `chore: update requirements.txt with psycopg2-binary`      |
| `db:`           | Migracions i canvis d'esquema                   | `db: add audit_logs trigger for patients table`            |

### Freqüència de commits

S'han realitzat **més de 60 commits** al llarg del projecte, amb una mitjana de 5-6 commits per sessió de treball. Cada commit representa un canvi atòmic i funcional, evitant commits massius que barregin múltiples canvis no relacionats.

### Fitxer de configuració de GitHub

El repositori inclou els següents fitxers de configuració:

- `.gitignore` — Exclou `.env`, `__pycache__/`, `*.pyc`, fitxers de certificats i dades temporals
- `.gitattributes` — Configuració de final de línia per a Windows/Linux

## Resum de dedicació

El projecte ha requerit un total de **91 hores reals** enfront de les **77 hores estimades**, la qual cosa representa una desviació del **+18,2%**.

### Anàlisi de desviacions

| Tasca                    | Est. | Real | Desv. | Causa principal                                              |
| ------------------------ | ---- | ---- | ----- | ------------------------------------------------------------ |
| Alta disponibilitat      | 10   | 14   | +40%  | Corba d'aprenentatge amb replicació PostgreSQL i configuració de Tailscale |
| Bloc de manteniment      | 10   | 12   | +20%  | Complexitat no prevista en les relacions N:M entre entitats  |
| Exportació de dades      | 8    | 10   | +25%  | Integració amb Chart.js i generació de gràfics dinàmics      |
| Altres                   | 49   | 55   | +12%  | Petit marge en tasques individuals                           |

Les desviacions es concentren en tasques que implicaven tecnologies no cobertes a classe (Tailscale, replicació de bases de dades, Chart.js). Per a futures planificacions, seria recomanable augmentar el marge de contingència en tasques que impliquen aprenentatge de noves eines.

## Diari de sessions

Seguiment diari a la tasca de Moodle. A continuació es resumeixen les sessions principals:

| Data       | Hores | Tasques realitzades                                          |
| ---------- | ----- | ------------------------------------------------------------ |
| 01/04/2026 | 3     | Configuració inicial del repositori, estructura de carpetes  |
| 06/04/2026 | 4     | Connexió a PostgreSQL, models SQLAlchemy bàsics              |
| 08/04/2026 | 3     | Endpoints de login i registre, proves amb curl               |
| 10/04/2026 | 4     | Disseny ER, definició de 24 taules, normalització            |
| 15/04/2026 | 5     | Creació de rols de base de dades, RLS, scripts de seguretat  |
| 18/04/2026 | 4     | CRUD de personal mèdic i pacients                            |
| 22/04/2026 | 6     | Replicació PostgreSQL, configuració Tailscale entre nodes    |
| 27/04/2026 | 6     | CRUD de visites, cirurgies, admissions                       |
| 02/05/2026 | 4     | Informes i reports bàsics                                    |
| 06/05/2026 | 5     | Generació de dummy data, càrrega massiva                     |
| 09/05/2026 | 7     | Dashboard Chart.js, exportació XML/JSON                      |
| 13/05/2026 | 5     | Documentació d'instal·lació i manual d'usuari                |
| 17/05/2026 | 3     | Document final, revisió global                               |
| **Total**  | **59**| (91 h totals, la resta són hores complementàries de reforç)  |

## Lliçons apreses i millores de futur

1. **Planificació conservadora:** Les tasques amb tecnologies noves haurien de tenir un marge del 40-50% addicional.
2. **Commits atòmics:** La disciplina de commits reduïts i descriptius ha facilitat molt la revisió de canvis i la depuració.
3. **Documentació integrada:** Mantenir la documentació al mateix repositori (no a Moodle) ha permès tenir-la sempre actualitzada i versionada.
4. **Tailscale vs VPN tradicional:** Tailscale ha simplificat enormement la connectivitat entre nodes, evitant la configuració de routers i ports oberts.
