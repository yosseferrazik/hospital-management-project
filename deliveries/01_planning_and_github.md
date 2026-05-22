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

| Tasca                           | Subtasca                                            | Data inici | Data fi    | Hores est. | Hores reals | Responsable |
| ------------------------------- | --------------------------------------------------- | ---------- | ---------- | ---------- | ----------- | ----------- |
| **Planificació**                | Definir grups, eines i planificació                 | 01/04/2026 | 09/04/2026 | 4          | 5           | Yossef      |
| **Connectivitat i login**       | Connexió BD, registre, login, fitxer de credencials | 06/04/2026 | 13/04/2026 | 6          | 7           | Yossef      |
| **ER - Model Relacional**       | Diagrama ER, model relacional, SQL                  | 06/04/2026 | 15/04/2026 | 5          | 6           | Yossef      |
| **Esquema de seguretat**        | Rols, RLS, SSL, data masking, AGPD                  | 15/04/2026 | 22/04/2026 | 8          | 9           | Yossef      |
| **Bloc de manteniment**         | CRUD personal, pacients, visites, cirurgies         | 13/04/2026 | 27/04/2026 | 10         | 12          | Yossef      |
| **Alta disponibilitat**         | Replicació, backups, restore, monitorització        | 22/04/2026 | 06/05/2026 | 10         | 14          | Yossef      |
| **Bloc de consultes**           | Informes i reports                                  | 27/04/2026 | 09/05/2026 | 8          | 8           | Yossef      |
| **Dummy Data**                  | Generació de dades falses, càrrega massiva          | 06/05/2026 | 13/05/2026 | 6          | 7           | Yossef      |
| **Exportació de dades**         | XML/JSON, XSD, API Seguretat Social, Dashboard      | 09/05/2026 | 17/05/2026 | 8          | 10          | Yossef      |
| **Document final instal·lació** | Guia d'instal·lació completa                        | 13/05/2026 | 20/05/2026 | 4          | 5           | Yossef      |
| **Manual d'usuari**             | Guia d'ús de l'aplicació                            | 13/05/2026 | 20/05/2026 | 4          | 4           | Yossef      |
| **Document final**              | Recopilatori de tot el projecte                     | 17/05/2026 | 20/05/2026 | 4          | 4           | Yossef      |

## Resum de dedicació

El projecte ha requerit un total de **91 hores reals** enfront de les **77 hores estimades**, la qual cosa representa una desviació del +18%. Les tasques que han requerit més hores de les previstes han estat les d'alta disponibilitat (14 h reals vs 10 h est.) i el bloc de manteniment (12 h reals vs 10 h est.), principalment degut a la corba d'aprenentatge amb tecnologies noves i la resolució de problemes imprevistos durant la implementació.

## Diari de sessions

Seguiment diari a la tasca de Moodle.
