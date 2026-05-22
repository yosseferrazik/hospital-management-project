# 8. BD — Dummy Data

## Visió general

Generació de dades falses per a proves de rendiment i validació de l'aplicació utilitzant la llibreria **Faker** (locale `es_ES` i `ru_RU`). El sistema de generació de dades de prova permet poblar la base de dades amb grans volums d'informació realista per verificar el comportament de l'aplicació sota càrrega.

**Ubicació del generador:** `server/src/app/services/dummy_service.py`

**Activació:** Des de l'aplicació d'escriptori: menú **Dummy Data** → configurar quantitat → **Generate**

## Volums de dades

Requisits del projecte i valors assolits:

| Entitat          | Quantitat objectiu   | Generat                             |
| ---------------- | -------------------- | ----------------------------------- |
| Pacients         | 50.000               | 50.000                              |
| Visites          | 100.000              | 100.000+ (2× pacients)              |
| Metges           | 100                  | 100                                 |
| Infermeres       | 200                  | 200                                 |
| Personal general | 100                  | 100 (50 administratius + 50 neteja) |
| Cirurgies        | ~25.000              | ~25.000                             |
| Admissions       | ~25.000              | ~25.000                             |
| Prescripcions    | Enllaçades a visites | Generades proporcionalment          |

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/dummy_data/2026-05-22-18-29-38-image.png)

## Procés de generació

1. **Dades de suport** (especialitats, medicaments, plantes, habitacions, quiròfans, dispositius) es creen primer
2. **Staff**: metges amb especialitats, infermeres amb metge/planta assignat, personal general
3. **Pacients**: noms, adreces i telèfons realistes espanyols
4. **Visites**: distribuïdes en els últims 60 dies (algunes al futur per a visites programades), amb diagnòstics per especialitat
5. **Cirurgies, admissions, prescripcions, dispensacions, radiologia**: generades proporcionalment

## Dades en ciríl·lic

Aproximadament el **5%** dels pacients i staff tenen noms en alfabet ciríl·lic (generats amb Faker locale `ru_RU`) per complir el requisit de suport a pacients de l'Europa de l'Est. Aquesta característica demostra la capacitat de la base de dades per treballar amb caràcters multibyte (UTF-8).

## Optimització de rendiment

La generació inicial de 50.000 pacients i 100.000 visites era lenta (~20 minuts). Es va optimitzar:

- **Insercions per lots** amb `flush()` cada 20 registres i `commit()` cada 400, reduint el temps total a aproximadament 5 minuts
- **Pools de diagnòstics** pre-calculats per especialitat, evitant consultes repetitives
- **Mostreig aleatori** en lloc d'iteració seqüencial per millorar la distribució de les dades

## Neteja

Una taula `DummyRegistry` rastreja tots els registres generats. L'opció **Cleanup dummy data** de l'aplicació d'escriptori elimina tot en ordre invers de dependències i neteja el registre. Això garanteix que no quedin restes de dades de prova al sistema.

## Com executar

Des de l'aplicació d'escriptori:

1. Iniciar sessió com a admin
2. Obrir **Dummy Data** des de la barra lateral
3. Introduir nombre de pacients (màx. 50.000)
4. Fer clic a **Generate**

També des de l'API:

```bash
POST /api/dummy/generate
Body: {"patient_count": 50000}
```

## Referències

- `docs/02_database/test_data.md` — Documentació completa
- `server/src/app/services/dummy_service.py` — Codi font del generador
- `scripts/sql/schema.sql` — Esquema amb índexs per a rendiment
