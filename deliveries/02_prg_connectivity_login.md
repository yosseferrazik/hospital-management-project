# 2. PRG — Bloc de Connectivitat i Login

## Connexió a la base de dades

L'aplicació es connecta a PostgreSQL 16 des de Python utilitzant **psycopg2-binary** (driver natiu C) i **SQLAlchemy 2.0** com a ORM. La connexió es fa mitjançant una cadena de connexió emmagatzemada en variable d'entorn, evitant exposar credencials al codi font.

**Cadena de connexió** (variable d'entorn `DATABASE_URL`):

```
postgresql://postgres:********@localhost:5432/hsp_db
```

### Connection pooling

SQLAlchemy incorpora un pool de connexions per defecte (`QueuePool`) que gestiona de forma eficient les connexions a la base de dades:

| Paràmetre          | Valor | Descripció                                        |
| ------------------ | ----- | ------------------------------------------------- |
| `pool_size`        | 5     | Nombre màxim de connexions mantingudes obertes    |
| `max_overflow`     | 10    | Connexions addicionals permeses sota demanda      |
| `pool_timeout`     | 30    | Temps d'espera màxim per obtindre connexió (s)    |
| `pool_recycle`     | 1800  | Temps màxim de vida d'una connexió (s)            |
| `pool_pre_ping`    | True  | Verifica salut de la connexió abans d'usar-la     |

### Application factory

L'objecte `db` de SQLAlchemy es crea a `server/src/app/models.py` i s'inicialitza al patró *application factory*. Aquest enfocament permet canviar la configuració de la base de dades sense modificar el codi, simplement actualitzant la variable d'entorn.

```python
# server/src/app/__init__.py
def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()

    return app
```

## Registre i inici de sessió

### Flux de login

El procés d'autenticació segueix un flux segur en 6 passos:

1. L'usuari introdueix usuari i contrasenya al client Tkinter

   ![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/connectivity_login/2026-05-22-17-16-00-image.png)

2. El client fa una petició `POST /api/auth/login` amb les credencials
3. El servidor valida contra la taula `APP_USERS` (contrasenyes hashejades amb bcrypt)
4. Si les credencials són correctes, retorna un **JWT token** amb el rol i el `staff_id`
5. El client emmagatzema el token en memòria (singleton de sessió)
6. Per a totes les peticions posteriors, s'envia com a `Authorization: Bearer <token>`

### Estructura del JWT token

El token JWT conté les següents claims en el payload:

```json
{
  "sub": "admin",
  "role": "ADMIN",
  "staff_id": 1,
  "iat": 1716388800,
  "exp": 1716475200,
  "type": "access"
}
```

| Claim      | Descripció                                      |
| ---------- | ----------------------------------------------- |
| `sub`      | Nom d'usuari (identificador únic)               |
| `role`     | Rol d'usuari (ADMIN, DOCTOR, NURSE, etc.)       |
| `staff_id` | ID del membre del personal associat              |
| `iat`      | Data/hora d'emissió (issued at)                 |
| `exp`      | Data/hora d'expiració (3600s = 1 hora)          |
| `type`     | Tipus de token (access / refresh)               |

### Hashing de contrasenyes amb bcrypt

bcrypt és un algoritme d'hashing de contrasenyes dissenyat específicament per a emmagatzematge segur. Les seves característiques principals:

- **Salt automàtic:** Cada hash incorpora un salt aleatori de 16 bytes, garantint que contrasenyes idèntiques generin hashes diferents.
- **Work factor (cost):** El paràmetre `rounds` (per defecte 12 en aquest projecte) controla el nombre d'iteracions de l'algoritme, fent-lo resistent a atacs de força bruta.
- **Resistent a ASIC/GPU:** A diferència de SHA-256 o MD5, bcrypt requereix memòria i és difícil d'optimitzar en hardware especialitzat.

```python
# Exemple d'ús a server/src/app/routes/auth.py
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# Hash al registrar
hashed = bcrypt.generate_password_hash(password).decode('utf-8')

# Verificació al login
if not bcrypt.check_password_password(user.password_hash, password):
    return {"error": "Credencials invàlides"}, 401
```

### Exemple de login

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

### Gestió de sessions al client

El client Tkinter implementa un **singleton de sessió** que manté l'estat d'autenticació durant tota la vida de l'aplicació:

```python
# server/src/app/session.py (client-side singleton)
class SessionManager:
    _instance = None
    _token = None
    _user = None
    _role = None
    _staff_id = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def login(self, token, user, role, staff_id):
        self._token = token
        self._user = user
        self._role = role
        self._staff_id = staff_id

    @property
    def auth_header(self):
        return {"Authorization": f"Bearer {self._token}"}

    def logout(self):
        self._token = self._user = self._role = self._staff_id = None
```

Totes les peticions HTTP posteriors del client inclouen automàticament la capçalera `Authorization` mitjançant el mètode `auth_header` del singleton.

## Fitxer de credencials

Les credencials **NO** es guarden en un fitxer pla. L'emmagatzematge és:

- **Base de dades PostgreSQL:** la taula `APP_USERS` conté els usuaris amb contrasenya hashejada amb **bcrypt** (mai en text pla)
- **Variables d'entorn:** el secret JWT es carrega des de `/etc/hms.env` (propietat root:root, permisos 600)
- **Token en memòria:** el client guarda el JWT en una variable en memòria (no en disc)

### Exemple de `/etc/hms.env`

```env
# Aquest fitxer NO es puja al repositori. Permisos: 600
DATABASE_URL=postgresql://postgres:password_real@localhost:5432/hsp_db
JWT_SECRET_KEY=una_clau_secreta_de_256_bits_generada_amb_secrets_token_hex
FLASK_ENV=production
MAIL_SERVER=smtp.hospital.cat
```

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
