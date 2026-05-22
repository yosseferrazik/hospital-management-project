# 2. PRG — Bloc de Connectivitat i Login

## Connexió a la base de dades

L'aplicació es connecta a PostgreSQL 16 des de Python utilitzant **psycopg2-binary** i **SQLAlchemy 2.0**. La connexió es fa mitjançant una cadena de connexió emmagatzemada en variable d'entorn, evitant exposar credencials al codi font.

**Cadena de connexió** (variable d'entorn `DATABASE_URL`):

```
postgresql://postgres:********@localhost:5432/hsp_db
```

L'objecte `db` de SQLAlchemy es crea a `server/src/app/models.py` i s'inicialitza al patró *application factory*. Aquest enfocament permet canviar la configuració de la base de dades sense modificar el codi, simplement actualitzant la variable d'entorn.

## Registre i inici de sessió

### Flux de login

El procés d'autenticació segueix un flux segur en 6 passos:

1. L'usuari introdueix usuari i contrasenya al client Tkinter
   
   ![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/connectivity_login/2026-05-22-17-16-00-image.png)

2. El client fa una petició `POST /api/auth/login` amb les credencials
3. El servidor valida contra la taula `APP_USERS` (contrasenyes hashejades amb bcrypt)
4. Si les credencials són correctes, retorna un **JWT token** amb el rol i el staff_id
5. El client emmagatzema el token en memòria (singleton de sessió)
6. Per a totes les peticions posteriors, s'envia com a `Authorization: Bearer <token>`

### Exemple

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "*****"}'

# Resposta
{"access_token": "eyJhbGciOiJIUzI1NiIs...", "role": "ADMIN", "staff_id": 1}
```

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/connectivity_login/2026-05-22-17-20-44-image.png)

### Endpoints d'autenticació

| Mètode | Endpoint                             | Autenticació | Descripció                             |
| ------ | ------------------------------------ | ------------ | -------------------------------------- |
| POST   | `/api/auth/login`                    | No           | Inici de sessió, retorna token + rol   |
| POST   | `/api/auth/register`                 | No           | Crear nou usuari                       |
| GET    | `/api/auth/users`                    | JWT          | Llistar usuaris                        |
| PUT    | `/api/auth/change-password`          | JWT          | Canviar pròpia contrasenya             |
| PUT    | `/api/auth/users/<id>/password`      | JWT+ADMIN    | Resetear contrasenya d'un altre usuari |
| PUT    | `/api/auth/users/<id>/toggle-active` | JWT+ADMIN    | Activar/desactivar compte              |

## Fitxer de credencials

Les credencials NO es guarden en un fitxer pla. L'emmagatzematge és:

- **Base de dades PostgreSQL**: la taula `APP_USERS` conté els usuaris amb contrasenya hashejada amb **bcrypt** (mai en text pla)
- **Variables d'entorn**: el secret JWT es carrega des de `/etc/hms.env` (propietat root:root, permisos 600)
- **Token en memòria**: el client guarda el JWT en una variable en memòria (no en disc)

## Seguretat aplicada

| Mesura                   | Implementació                                           |
| ------------------------ | ------------------------------------------------------- |
| Hashing de contrasenyes  | bcrypt (5.0.0) — `hashpw()` + `checkpw()`               |
| Tokens JWT               | Flask-JWT-Extended 4.7.1 — signats amb clau de 256 bits |
| Secrets en fitxer extern | `/etc/hms.env` — exclòs del repositori                  |
| Comptes desactivats      | `is_active = False` — denegats al login                 |
| Rols                     | 5 rols: ADMIN, DOCTOR, NURSE, STAFF, RECEPTIONIST       |

## Codi font rellevant

- `server/src/app/models.py` — Model `AppUser`
- `server/src/app/routes/auth.py` — Blueprint d'autenticació
- `server/src/app/config.py` — Config des de variables d'entorn
- `server/src/app/__init__.py` — App factory amb inicialització JWT
- `server/src/.env` — Fitxer d'entorn local (gitignored)
