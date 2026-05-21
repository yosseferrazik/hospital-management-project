import random
import math
from datetime import datetime, timedelta, timezone

from faker import Faker

from app.models import (
    Admission, DispensationItem, DummyRegistry, Floor, GeneralStaff,
    MedicalDevice, MedicalSpecialty, MedicalStaff, MedicalStaffSpecialty,
    Medication, NursingStaff, OperatingTheater, Patient,
    PharmacyDispensation, Prescription, RadiologyExam, Room,
    ScheduledAppointment, Staff, Surgery, SurgeryAssistant, Visit, db,
)

fake = Faker("es_ES")
fake_ru = Faker("ru_RU")
BATCH = 1000

MEDICAL_SPECIALTIES = [
    ("Cardiologia", "Diagnostico y tratamiento de enfermedades del corazon y el sistema circulatorio"),
    ("Neurologia", "Trastornos del sistema nervioso central y periferico"),
    ("Traumatologia", "Lesiones del sistema musculoesqueletico y fracturas"),
    ("Pediatria", "Atencion medica integral de pacientes infantiles y adolescentes"),
    ("Neumologia", "Enfermedades del aparato respiratorio y pulmonares"),
    ("Digestivo", "Trastornos del aparato digestivo y hepatologia"),
    ("Urologia", "Patologias del sistema urinario y aparato reproductor masculino"),
    ("Oftalmologia", "Enfermedades oculares y cirugia refractiva"),
    ("Dermatologia", "Trastornos de la piel, uñas y mucosas"),
    ("Endocrinologia", "Trastornos metabolicos y del sistema endocrino"),
    ("Rehabilitacion", "Medicina fisica y rehabilitacion funcional"),
    ("Oncologia", "Diagnostico y tratamiento del cancer"),
    ("Nefrologia", "Enfermedades renales y trastornos hidroelectroliticos"),
    ("Reumatologia", "Enfermedades autoinmunes y reumaticas"),
    ("Ginecologia", "Salud femenina y patologia del aparato reproductor"),
    ("Psiquiatria", "Trastornos de la salud mental y del comportamiento"),
]

MEDICATIONS = [
    ("Paracetamol 650mg", "Analgesico y antipiretico de uso frecuente"),
    ("Ibuprofeno 600mg", "Antiinflamatorio no esteroideo para dolor y fiebre"),
    ("Amoxicilina 500mg", "Antibiotico betalactamico para infecciones bacterianas"),
    ("Omeprazol 20mg", "Inhibidor de la bomba de protones para proteccion gastrica"),
    ("Atorvastatina 20mg", "Estatina para reduccion del colesterol LDL"),
    ("Enalapril 10mg", "Inhibidor de la ECA para hipertension arterial"),
    ("Metformina 850mg", "Antidiabetico oral para diabetes tipo 2"),
    ("Salbutamol Inhalador", "Broncodilatador de accion rapida para asma"),
    ("Losartan 50mg", "Antagonista de receptores de angiotensina II"),
    ("Omeprazol 40mg", "Inhibidor de bomba de protones de alta dosis"),
    ("Diazepam 5mg", "Ansiolitico benzodiacepina de accion prolongada"),
    ("Metamizol 575mg", "Analgesico y antipiretico de potencia moderada"),
    ("Heparina 5000UI", "Anticoagulante parenteral para profilaxis tromboembolica"),
    ("Furosemida 40mg", "Diuretico de asa para insuficiencia cardiaca"),
    ("Levofloxacino 500mg", "Antibiotico fluoroquinolona de amplio espectro"),
    ("Prednisona 30mg", "Corticoesteroide sistemico antiinflamatorio"),
    ("Acido Folico 5mg", "Suplemento vitaminico para anemias megaloblasticas"),
    ("Hierro Oral 100mg", "Suplemento de hierro para anemia ferropenica"),
    ("Insulina Glargina", "Insulina de accion prolongada para diabetes"),
    ("Morfina 10mg", "Analgesico opioide para dolor severo"),
    ("Bisoprolol 5mg", "Betabloqueante cardioselectivo para insuficiencia cardiaca"),
    ("Clopidogrel 75mg", "Antiplaquetario para prevencion de eventos cardiovasculares"),
    ("Warfarina 5mg", "Anticoagulante oral para fibrilacion auricular"),
    ("Fluoxetina 20mg", "Inhibidor selectivo de recaptacion de serotonina"),
    ("Pantoprazol 40mg", "Inhibidor de bomba de protones intravenoso"),
]

DIAGNOSES_BY_SPECIALTY = {
    "Cardiologia": [
        "Insuficiencia cardiaca congestiva descompensada",
        "Fibrilacion auricular no valvular",
        "Cardiopatia isquemica cronica",
        "Hipertension arterial esencial grado II",
        "Infarto agudo de miocardio sin elevacion ST",
        "Estenosis aortica severa sintomatica",
        "Miocardiopatia dilatada con FEVI reducida",
        "Pericarditis aguda idiopatica",
        "Tromboembolismo pulmonar bilateral",
        "Bloqueo auriculoventricular completo",
    ],
    "Neurologia": [
        "Accidente cerebrovascular isquemico agudo",
        "Migrana cronica con aura",
        "Enfermedad de Parkinson inicial",
        "Esclerosis multiple remitente-recurrente",
        "Neuropatia diabetica periferica",
        "Epilepsia focal refractaria",
        "Cefalea tensional cronica",
        "Demencia tipo Alzheimer de inicio tardio",
        "Polineuropatia desmielinizante inflamatoria cronica",
        "Sindrome del tunel carpiano bilateral",
    ],
    "Traumatologia": [
        "Fractura de femur proximal desplazada",
        "Rotura de ligamento cruzado anterior",
        "Artrosis de rodilla severa bilateral",
        "Fractura de radio distal con desplazamiento",
        "Hernia discal lumbar L4-L5",
        "Fractura de cadera osteoporotica",
        "Tendinitis rotuliana cronica",
        "Luxacion recidivante de hombro",
        "Fractura de tobillo bimaleolar",
        "Escoliosis lumbar degenerativa",
    ],
    "Pediatria": [
        "Bronquiolitis aguda por VRS",
        "Infeccion del tracto urinario febril",
        "Asma bronquial infantil persistente",
        "Neumonia adquirida en la comunidad",
        "Gastroenteritis aguda con deshidratacion",
        "Dermatitis atopica exacerbada",
        "Fiebre sin foco de origen viral",
        "Crisis asmatica moderada-grave",
        "Epiglotitis aguda por Haemophilus",
        "Convulsion febril simple",
    ],
    "Neumologia": [
        "EPOC exacerbado infeccioso",
        "Neumonia bilateral por neumococo",
        "Asma bronquial persistente severa",
        "Derrame pleural paraneumatico",
        "Fibrosis pulmonar idiopatica",
        "Tromboembolismo pulmonar segmentario",
        "Bronquiectasias bilaterales infectadas",
        "Sarcoidosis pulmonar estadio II",
        "Neumotorax espontaneo primario",
        "Sindrome de apnea-hipopnea del sueno severo",
    ],
    "Digestivo": [
        "Enfermedad por reflujo gastroesofagico erosiva",
        "Hepatitis aguda por virus B",
        "Pancreatitis aguda biliar leve",
        "Cirrosis hepatica descompensada con ascitis",
        "Colitis ulcerosa activa moderada",
        "Diverticulitis aguda no complicada",
        "Colelitiasis sintomatica con colecistitis",
        "Enfermedad de Crohn ileocolica",
        "Ulcera peptica duodenal activa",
        "Esteatosis hepatica no alcoholica",
    ],
    "Urologia": [
        "Hiperplasia benigna de prostata con retencion",
        "Litiasis renal proximal sintomatica",
        "Infeccion urinaria recurrente complicada",
        "Cancer de prostata localizado Gleason 6",
        "Pielonefritis aguda bacteriurica",
        "Estenosis de uretra bulbar",
        "Tumor vesical superficial no invasivo",
        "Prostatitis cronica bacteriana",
        "Hidronefrosis por obstruccion ureteral",
        "Criptorquidia unilateral",
    ],
    "Oftalmologia": [
        "Catarata senil bilateral madura",
        "Glaucoma cronico de angulo abierto",
        "Desprendimiento de retina regmatogeno",
        "Retinopatia diabetica proliferativa",
        "Ojo seco severo evaporativo",
        "Membrana epirretiniana sintomatica",
        "Queratocono avanzado bilateral",
        "Uveitis anterior aguda idiopatica",
        "Degeneracion macular asociada a la edad humeda",
        "Obstruccion de vena central de retina",
    ],
    "Dermatologia": [
        "Psoriasis en placas cronica severa",
        "Dermatitis atopica del adulto exacerbada",
        "Melanoma maligno superficial de espalda",
        "Celulitis infecciosa de miembro inferior",
        "Acne noduloquistico facial severo",
        "Carcinoma basocelular nodular nasal",
        "Urticaria cronica espontanea severa",
        "Micosis fungoides estadio IA",
        "Rosacea papulopustular moderada",
        "Liquen plano cutaneo generalizado",
    ],
    "Endocrinologia": [
        "Diabetes mellitus tipo 2 descompensada",
        "Hipotiroidismo primario autoinmune",
        "Hipertiroidismo por enfermedad de Graves",
        "Sindrome de Cushing ACTH-dependiente",
        "Diabetes mellitus tipo 1 debut cetosico",
        "Hiperaldosteronismo primario bilateral",
        "Feocromocitoma suprarrenal unilateral",
        "Osteoporosis severa con fractura vertebral",
        "Hiperparatiroidismo secundario renal",
        "Sindrome metabolico con obesidad severa",
    ],
    "Rehabilitacion": [
        "Hemiplejia izquierda post-ictus",
        "Contractura muscular cronica cervical",
        "Readaptacion tras artroplastia de rodilla",
        "Linfedema post-mastectomia severo",
        "Lesion medular incompleta subcervical",
        "Sindrome de dolor regional complejo tipo I",
        "Disfuncion del suelo pelvico",
        "Dorsalgia cronica mecanica",
        "Paralisis facial periferica aguda",
        "Fibromialgia con impacto funcional severo",
    ],
    "Oncologia": [
        "Cancer de mama infiltrante ductal",
        "Neoplasia pulmonar de celulas no pequenas",
        "Cancer colorrectal estadio III",
        "Linfoma difuso de celulas B grandes",
        "Tumor de ovario seroso papilar",
        "Mieloma multiple IgG kappa",
        "Cancer gastrico avanzado HER2 negativo",
        "Sarcoma de partes blandas de muslo",
        "Leucemia linfoblastica aguda L1",
        "Carcinoma hepatocelular sobre cirrosis",
    ],
    "Nefrologia": [
        "Enfermedad renal cronica estadio 4",
        "Nefropatia diabetica con proteinuria",
        "Sindrome nefrotico primario minimo cambio",
        "Insuficiencia renal aguda prerrenal",
        "Glomerulonefritis membranoproliferativa",
        "Hipertension renovascular unilateral",
        "Nefritis lupica clase IV",
        "Poliquistosis renal autosomica dominante",
        "Nefritis tubulointersticial aguda",
        "Acidosis tubular renal distal",
    ],
    "Reumatologia": [
        "Artritis reumatoide seropositiva activa",
        "Lupus eritematoso sistemico con afectacion renal",
        "Artritis gotosa aguda de primer metatarsiano",
        "Espondilitis anquilosante activa",
        "Sindrome de Sjogren primario",
        "Vasculitis ANCA-positiva limitada",
        "Polimialgia reumatica de inicio agudo",
        "Esclerodermia sistemica difusa",
        "Artritis psoriasica oligoarticular",
        "Fiebre mediterranea familiar",
    ],
    "Ginecologia": [
        "Miomatosis uterina sintomatica multiple",
        "Endometriosis ovarica bilateral profunda",
        "Infeccion vaginal recurrente por Candida",
        "Sangrado uterino anormal disfuncional",
        "Quiste ovarico hemorragico complicado",
        "Enfermedad inflamatoria pelvica aguda",
        "Prolapso uterino grado III",
        "Hiperplasia endometrial compleja",
        "Amenorrea secundaria de origen hipotalamico",
        "Embarazo ectopico tubarico no roto",
    ],
    "Psiquiatria": [
        "Trastorno depresivo mayor recurrente",
        "Trastorno de ansiedad generalizada cronico",
        "Trastorno bipolar tipo I episodio maniaco",
        "Trastorno obsesivo-compulsivo de lavado",
        "Trastorno de panico con agorafobia",
        "Esquizofrenia paranoide primer episodio",
        "Trastorno por deficit de atencion adulto",
        "Trastorno de estres postraumatico complejo",
        "Trastorno limite de la personalidad",
        "Anorexia nerviosa restrictiva severa",
    ],
}

SURGERY_PROCEDURES = [
    "Revascularizacion miocardica con injerto",
    "Reemplazo valvular aortico mecanico",
    "Angioplastia coronaria con stent farmacoactivo",
    "Artroplastia total de cadera cementada",
    "Artroplastia total de rodilla no cementada",
    "Osteosintesis de femur proximal con clavo",
    "Laminectomia descompresiva L4-L5",
    "Fusion intersomatica lumbar instrumentada",
    "Reconstruccion de ligamento cruzado anterior",
    "Reparacion de manguito rotador artroscopica",
    "Colecistectomia laparoscopica",
    "Herniorrafia inguinal con malla",
    "Prostatectomia radical laparoscopica",
    "Nefrolitotomia percutanea",
    "Reseccion transuretral de prostata",
    "Mastectomia radical modificada",
    "Lobectomia pulmonar videoasistida",
    "Colectomia derecha laparoscopica",
    "Reseccion anterior baja de recto",
    "Tiroidectomia total extracapsular",
    "Cesarea segmentaria transversa",
    "Histerectomia total abdominal",
    "Craneotomia por tumor cerebral",
    "Derivacion ventriculoperitoneal",
    "Facoemulsificacion con lente intraocular",
    "Trabeculectomia con mitomicina C",
]

RADIOLOGY_EXAMS = [
    "Radiografia de torax PA y lateral",
    "Radiografia de columna lumbar AP y lateral",
    "Radiografia de rodilla AP y lateral con carga",
    "Radiografia de cadera AP axial",
    "Radiografia de mano y muñeca PA",
    "Resonancia magnetica de columna lumbar",
    "Resonancia magnetica de rodilla sin contraste",
    "Resonancia magnetica cerebral sin contraste",
    "Resonancia magnetica de hombro con contraste",
    "Tomografia computarizada de torax con contraste",
    "Tomografia computarizada abdominal sin contraste",
    "Tomografia computarizada craneal simple",
    "Tomografia computarizada de pelvis con contraste",
    "Ecografia abdominal completa",
    "Ecografia de partes blandas",
    "Ecografia doppler de troncos supraaorticos",
    "Ecografia renal y de vias urinarias",
    "Ecocardiograma transtoracico",
    "Ecocardiograma de estres con dobutamina",
    "Mamografia bilateral digital",
    "Densitometria osea central",
    "Angiografia coronaria diagnostica",
    "Colonografia por tomografia computarizada",
    "PET-TC con FDG para estadificacion oncologica",
]

RADIOLOGY_FINDINGS = [
    "Sin hallazgos patologicos significativos",
    "Engrosamiento intersticial bilateral basal sugestivo de fibrosis",
    "Nodulo pulmonar solitario en lobulo superior derecho de 12mm",
    "Fractura completa de femur proximal con desplazamiento",
    "Hernia discal posterolateral L4-L5 con compromiso radicular",
    "Rotura completa de ligamento cruzado anterior con derrame",
    "Imagen litiasica de 8mm en tercio proximal ureteral",
    "Tumoracion renal derecha de 45mm sugestiva de carcinoma",
    "Colelitiasis multiple con barro biliar y pared vesicular engrosada",
    "Quiste ovarico izquierdo simple de 35mm sin componentes solidos",
    "Esteatosis hepatica moderada difusa sin focalidad",
    "Adenopatias mediastinicas multiples de aspecto reactivo",
    "Lesion ocupante de espacio en lobulo temporal izquierdo",
    "Derrame pleural derecho moderado sin engrosamientos",
    "Osteofitos marginales y pinzamiento articular femorotibial interno",
    "Infarto lacunar cronico en ganglios basales derechos",
    "Imagen especulada de 18mm en cuadrante superior externo mama izquierda",
    "Colon descendente con diverticulos sin signos de inflamacion",
    "Litiasis vesicular multiple, pared vesicular de 4mm",
    "Reflujo vesicoureteral bilateral grado II",
]

ADMISSION_REASONS = [
    "Dolor toracico con sospecha de sindrome coronario agudo",
    "Disnea progresiva con signos de insuficiencia cardiaca",
    "Fractura de cadera con necesidad de intervencion quirurgica",
    "Neumonia adquirida en la comunidad con hipoxemia",
    "Accidente cerebrovascular agudo para monitorizacion",
    "Crisis hipertensiva con afectacion de organo diana",
    "Pancreatitis aguda biliar para manejo conservador",
    "Infeccion urinaria complicada con sepsis",
    "Crisis asmatica severa que requiere oxigenoterapia",
    "Hemorragia digestiva alta con inestabilidad hemodinamica",
    "Descompensacion de diabetes mellitus con cetoacidosis",
    "Insuficiencia renal aguda para reposicion hidroelectrolitica",
    "Colecistitis aguda para colecistectomia urgente",
    "Tromboembolismo pulmonar para anticoagulacion",
    "Reagudizacion de EPOC con insuficiencia respiratoria",
    "Fiebre sin foco de origen en paciente inmunodeprimido",
]

ALLERGIES_LIST = [
    "", "", "", "",
    "Penicilinas (amoxicilina, ampicilina)",
    "Antiinflamatorios no esteroideos (ibuprofeno, aspirina)",
    "Sulfamidas (cotrimoxazol)",
    "Contraste yodado intravenoso",
    "Latex",
    "Huevo y derivados (propofol)",
    "Codeina y opioides menores",
    "Corticoesteroides topicos",
    "Hierro dextrano intravenoso",
    "Penicilinas y cefalosporinas",
    "Anestésicos locales (lidocaina)",
    "Protamina",
]


def _register(table_name, record_id):
    db.session.add(DummyRegistry(table_name=table_name, record_id=record_id))


def _random_birth_date(min_age=22, max_age=85):
    age = random.randint(min_age, max_age)
    return datetime.now(timezone.utc).date() - timedelta(days=age * 365 + random.randint(0, 300))


def _unique_email(prefix):
    return f"{prefix}.{fake.unique.lexify(text='??????')}@salutpalomera.test"


def _cyrillic_name():
    if random.random() < 0.05:
        return fake_ru.first_name(), fake_ru.last_name()
    return fake.first_name(), fake.last_name()

def _cyrillic_word():
    if random.random() < 0.05:
        return fake_ru.text(max_nb_chars=80)
    return ""

def _flush_batch(committed=0):
    db.session.flush()
    committed += 1
    if committed % 20 == 0:
        db.session.commit()
    return committed


def _ensure_support_data():
    specialty_map = {}
    for name, desc in MEDICAL_SPECIALTIES:
        existing = MedicalSpecialty.query.filter_by(name=name).first()
        if existing:
            specialty_map[name] = existing
            continue
        s = MedicalSpecialty(name=name, description=desc)
        db.session.add(s)
        db.session.flush()
        _register("medical_specialties", s.specialty_id)
        specialty_map[name] = s
    db.session.commit()

    floors = Floor.query.all()
    if not floors:
        for number in range(1, 6):
            floor = Floor(floor_number=number)
            db.session.add(floor)
            db.session.flush()
            _register("floors", floor.floor_id)
        db.session.commit()
        floors = Floor.query.all()

    rooms = Room.query.all()
    if not rooms:
        for floor in floors:
            for idx in range(1, 8):
                room = Room(room_number=f"{floor.floor_number}{idx:02d}", floor_id=floor.floor_id)
                db.session.add(room)
                db.session.flush()
                _register("rooms", room.room_id)
        db.session.commit()
        rooms = Room.query.all()

    theaters = OperatingTheater.query.all()
    if not theaters:
        for floor in floors[:3]:
            theater = OperatingTheater(theater_code=f"QUIRO-{floor.floor_number}", floor_id=floor.floor_id)
            db.session.add(theater)
            db.session.flush()
            _register("operating_theaters", theater.theater_id)
        db.session.commit()
        theaters = OperatingTheater.query.all()

    devices = MedicalDevice.query.all()
    if not devices:
        for theater in theaters:
            for device_name in ["Monitor multiparametrico", "Ventilador mecanico", "Electrobisturi", "Bomba de infusion"]:
                device = MedicalDevice(device_type=device_name, theater_id=theater.theater_id, quantity=random.randint(1, 3))
                db.session.add(device)
                db.session.flush()
                _register("medical_devices", device.device_id)
        db.session.commit()

    meds = Medication.query.all()
    if not meds:
        for name, desc in MEDICATIONS:
            m = Medication(medication_name=name, description=desc)
            db.session.add(m)
            db.session.flush()
            _register("medications", m.medication_id)
        db.session.commit()
        meds = Medication.query.all()

    return specialty_map, floors, Room.query.all(), OperatingTheater.query.all(), Medication.query.all()


def _create_staff_batch(specialty_map, patient_count):
    factor = max(1, math.ceil(patient_count / 1000))
    all_specialties = list(specialty_map.values())
    batch_committed = 0

    def _make_staff(staff_type):
        first_name, last_name = _cyrillic_name()
        s = Staff(
            national_id=fake.unique.numerify(text="########"),
            first_name=first_name,
            last_name=last_name,
            birth_date=_random_birth_date(),
            phone=fake.phone_number(),
            ssn=fake.unique.numerify(text="##########"),
            email=_unique_email(staff_type.lower()),
            address=fake.address(),
            staff_type=staff_type,
        )
        db.session.add(s)
        db.session.flush()
        _register("staff", s.staff_id)
        return s

    doctors = []
    for _ in range(10 * factor):
        staff = _make_staff("MEDICAL")
        specialty = random.choice(all_specialties)
        doctor = MedicalStaff(
            staff_id=staff.staff_id,
            specialty_id=specialty.specialty_id,
            license_number=f"MAD-{fake.unique.numerify(text='######')}",
            curriculum=f"Licenciado en Medicina, especialista en {specialty.name}. {fake.sentence(nb_words=12)}",
        )
        db.session.add(doctor)
        db.session.flush()
        _register("medical_staff", doctor.staff_id)
        mss = MedicalStaffSpecialty(staff_id=doctor.staff_id, specialty_id=specialty.specialty_id)
        db.session.add(mss)
        doctors.append(doctor)
        batch_committed = _flush_batch(batch_committed)

    nurses = []
    for _ in range(16 * factor):
        staff = _make_staff("NURSING")
        nurse = NursingStaff(
            staff_id=staff.staff_id,
            nursing_license=f"ENF-{fake.unique.numerify(text='######')}",
            assigned_doctor_id=random.choice(doctors).staff_id if doctors else None,
            assigned_floor_id=random.randint(1, 5),
            certifications=random.choice([
                "Enfermeria general, cuidados intensivos",
                "Enfermeria quirurgica, instrumentacion",
                "Enfermeria pediatrica, neonatologia",
                "Enfermeria geriatrica, cuidados paliativos",
                "Enfermeria de urgencias, triage avanzado",
                "Matrona, salud sexual y reproductiva",
            ]),
        )
        db.session.add(nurse)
        db.session.flush()
        _register("nursing_staff", nurse.staff_id)
        nurses.append(nurse)
        batch_committed = _flush_batch(batch_committed)

    general = []
    for _ in range(6 * factor):
        staff = _make_staff("GENERAL")
        person = GeneralStaff(
            staff_id=staff.staff_id,
            job_type=random.choice([
                "Recepcion", "Adminstracion", "Limpieza",
                "Mantenimiento", "Seguridad", "Cocina",
                "Archivo clinico", "Facturacion",
            ]),
        )
        db.session.add(person)
        db.session.flush()
        _register("general_staff", person.staff_id)
        general.append(person)
        batch_committed = _flush_batch(batch_committed)

    db.session.commit()
    return doctors, nurses, general


def _create_patients(count):
    patients = []
    batch_committed = 0
    for _ in range(count):
        first_name, last_name = _cyrillic_name()
        p = Patient(
            national_id=fake.unique.numerify(text="########"),
            first_name=first_name,
            last_name=last_name,
            birth_date=_random_birth_date(1, 90),
            gender=random.choice(["MALE", "FEMALE", "OTHER"]),
            phone=fake.phone_number(),
            email=_unique_email("patient"),
            address=fake.address(),
            emergency_contact_name=fake.name(),
            emergency_contact_phone=fake.phone_number(),
            blood_type=random.choice(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]),
            allergies=random.choice(ALLERGIES_LIST),
            health_card=fake.unique.numerify(text="##########"),
        )
        db.session.add(p)
        db.session.flush()
        _register("patients", p.patient_id)
        patients.append(p)
        batch_committed = _flush_batch(batch_committed)
    db.session.commit()
    return patients


def generate_dummy_data(patient_count=20):
    patient_count = max(1, min(patient_count, 50000))
    cleanup_dummy()

    specialty_map, floors, rooms, theaters, medications = _ensure_support_data()
    doctors, nurses, _general = _create_staff_batch(specialty_map, patient_count)
    patients = _create_patients(patient_count)

    specialty_names = {s.specialty_id: s.name for s in MedicalSpecialty.query.all()}

    visit_count = max(patient_count * 2, 30)
    visits = []
    for _ in range(visit_count):
        doctor = random.choice(doctors)
        spec_name = specialty_names.get(doctor.specialty_id, "Cardiologia")
        diag_pool = DIAGNOSES_BY_SPECIALTY.get(spec_name, DIAGNOSES_BY_SPECIALTY["Cardiologia"])
        cyr_note = _cyrillic_word()
        if cyr_note:
            notes = f"{fake.sentence(nb_words=12)} {cyr_note}"
        else:
            notes = fake.sentence(nb_words=15)
        visit = Visit(
            patient_id=random.choice(patients).patient_id,
            doctor_id=doctor.staff_id,
            visit_timestamp=fake.date_time_between(start_date="-60d", end_date="+5d"),
            diagnosis=random.choice(diag_pool),
            notes=notes,
        )
        db.session.add(visit)
        db.session.flush()
        _register("visits", visit.visit_id)
        visits.append(visit)
    db.session.commit()

    for visit in visits[:max(10, len(visits) // 2)]:
        appt = ScheduledAppointment(
            visit_id=visit.visit_id,
            appointment_date=visit.visit_timestamp.date() + timedelta(days=random.randint(0, 7)),
            appointment_time=(
                datetime.min + timedelta(
                    hours=random.randint(8, 18),
                    minutes=random.choice([0, 15, 30, 45])
                )
            ).time(),
            status=random.choice(["SCHEDULED", "COMPLETED", "COMPLETED", "COMPLETED", "CANCELLED", "NO_SHOW"]),
        )
        db.session.add(appt)
        db.session.flush()
        _register("scheduled_appointments", appt.appointment_id)
    db.session.commit()

    surgery_count = max(patient_count // 2, 10)
    surgeries = []
    for _ in range(surgery_count):
        start_hour = random.randint(7, 17)
        end_hour = start_hour + random.randint(1, 4)
        surgery = Surgery(
            patient_id=random.choice(patients).patient_id,
            theater_id=random.choice(theaters).theater_id,
            primary_surgeon_id=random.choice(doctors).staff_id,
            surgery_date=datetime.now(timezone.utc).date() + timedelta(days=random.randint(-30, 10)),
            start_time=(datetime.min + timedelta(hours=start_hour)).time(),
            end_time=(datetime.min + timedelta(hours=end_hour)).time(),
            procedure_type=random.choice(SURGERY_PROCEDURES),
            notes=f"Intervencion quirurgica programada. {fake.sentence(nb_words=10)}",
        )
        db.session.add(surgery)
        db.session.flush()
        _register("surgeries", surgery.surgery_id)
        surgeries.append(surgery)
    db.session.commit()

    for surgery in surgeries:
        for nurse in random.sample(nurses, k=min(2, len(nurses))):
            assistant = SurgeryAssistant(
                surgery_id=surgery.surgery_id,
                nurse_id=nurse.staff_id,
                role=random.choice(["Instrumentista", "Circulante"]),
            )
            db.session.add(assistant)
            db.session.flush()
            _register("surgery_assistants", surgery.surgery_id)
    db.session.commit()

    admission_count = max(patient_count // 2, 10)
    admissions = []
    for patient in patients[:admission_count]:
        a = Admission(
            patient_id=patient.patient_id,
            room_id=random.choice(rooms).room_id,
            admission_date=fake.date_time_between(start_date="-30d", end_date="now"),
            expected_discharge_date=datetime.now(timezone.utc).date() + timedelta(days=random.randint(2, 15)),
        )
        db.session.add(a)
        db.session.flush()
        _register("admissions", a.admission_id)
        admissions.append(a)
    db.session.commit()

    for visit in visits[:min(visit_count, len(visits))]:
        med = random.choice(medications)
        dosage_map = {m.medication_name: m for m in medications}
        chosen = dosage_map.get(med.medication_name, med)
        dosage_options = {
            "Paracetamol 650mg": "650mg",
            "Ibuprofeno 600mg": "600mg",
            "Amoxicilina 500mg": "500mg",
            "Omeprazol 20mg": "20mg",
            "Omeprazol 40mg": "40mg",
            "Atorvastatina 20mg": "20mg",
            "Enalapril 10mg": "10mg",
            "Metformina 850mg": "850mg",
            "Losartan 50mg": "50mg",
            "Diazepam 5mg": "5mg",
            "Metamizol 575mg": "575mg",
            "Furosemida 40mg": "40mg",
            "Levofloxacino 500mg": "500mg",
            "Prednisona 30mg": "30mg",
            "Acido Folico 5mg": "5mg",
            "Hierro Oral 100mg": "100mg",
            "Bisoprolol 5mg": "5mg",
            "Clopidogrel 75mg": "75mg",
            "Warfarina 5mg": "5mg",
            "Fluoxetina 20mg": "20mg",
            "Pantoprazol 40mg": "40mg",
        }
        dosage = dosage_options.get(chosen.medication_name, random.choice(["250mg", "500mg", "1g"]))
        freq = random.choice(["Cada 8 horas", "Cada 12 horas", "Cada 24 horas", "Cada 6 horas"])
        duration = random.choice([5, 7, 10, 14, 21])
        prescription = Prescription(
            visit_id=visit.visit_id,
            medication_id=chosen.medication_id,
            dosage=dosage,
            frequency=freq,
            duration_days=duration,
            start_date=datetime.now(timezone.utc).date(),
        )
        db.session.add(prescription)
        db.session.flush()
        _register("prescriptions", prescription.prescription_id)
    db.session.commit()

    for admission in admissions:
        disp = PharmacyDispensation(
            admission_id=admission.admission_id,
            dispensed_at=fake.date_time_between(start_date="-15d", end_date="now"),
            total_cost=round(random.uniform(15, 450), 2),
            notes=fake.sentence(nb_words=10),
        )
        db.session.add(disp)
        db.session.flush()
        _register("pharmacy_dispensations", disp.dispensation_id)

        for _ in range(random.randint(1, 4)):
            med = random.choice(medications)
            item = DispensationItem(
                dispensation_id=disp.dispensation_id,
                medication_id=med.medication_id,
                quantity=random.randint(1, 6),
                unit_price=round(random.uniform(3, 60), 2),
            )
            db.session.add(item)
            db.session.flush()
            _register("dispensation_items", item.item_id)
    db.session.commit()

    exam_count = max(patient_count, 15)
    for patient in patients[:exam_count]:
        doctor = random.choice(doctors)
        exam = RadiologyExam(
            patient_id=patient.patient_id,
            requesting_doctor_id=doctor.staff_id,
            exam_type=random.choice(RADIOLOGY_EXAMS),
            requested_at=fake.date_time_between(start_date="-30d", end_date="now"),
            performed_at=fake.date_time_between(start_date="-28d", end_date="now"),
            result_image_url=f"https://pacs.salutpalomera.test/estudios/{fake.uuid4()}",
            radiologist_report=random.choice(RADIOLOGY_FINDINGS),
            status=random.choice(["REQUESTED", "SCHEDULED", "COMPLETED", "COMPLETED", "COMPLETED", "CANCELLED"]),
        )
        db.session.add(exam)
        db.session.flush()
        _register("radiology_exams", exam.exam_id)
    db.session.commit()

    # ── set some actual_discharge dates on older admissions ──
    older = Admission.query.filter(
        Admission.admission_date < (datetime.now(timezone.utc) - timedelta(days=3))
    ).all()
    for adm in older:
        if random.random() < 0.7 and not adm.actual_discharge:
            adm.actual_discharge_date = adm.admission_date + timedelta(
                days=random.randint(1, 10)
            )
    db.session.commit()


def cleanup_dummy():
    registry_rows = DummyRegistry.query.order_by(DummyRegistry.id.desc()).all()
    if not registry_rows:
        return

    grouped = {}
    for row in registry_rows:
        grouped.setdefault(row.table_name, set()).add(row.record_id)

    for surgery_id in grouped.get("surgery_assistants", set()):
        SurgeryAssistant.query.filter_by(surgery_id=surgery_id).delete()
    for item_id in grouped.get("dispensation_items", set()):
        DispensationItem.query.filter_by(item_id=item_id).delete()
    for dispensation_id in grouped.get("pharmacy_dispensations", set()):
        PharmacyDispensation.query.filter_by(dispensation_id=dispensation_id).delete()
    for prescription_id in grouped.get("prescriptions", set()):
        Prescription.query.filter_by(prescription_id=prescription_id).delete()
    for appointment_id in grouped.get("scheduled_appointments", set()):
        ScheduledAppointment.query.filter_by(appointment_id=appointment_id).delete()
    for exam_id in grouped.get("radiology_exams", set()):
        RadiologyExam.query.filter_by(exam_id=exam_id).delete()
    for surgery_id in grouped.get("surgeries", set()):
        Surgery.query.filter_by(surgery_id=surgery_id).delete()
    for visit_id in grouped.get("visits", set()):
        Visit.query.filter_by(visit_id=visit_id).delete()
    for admission_id in grouped.get("admissions", set()):
        Admission.query.filter_by(admission_id=admission_id).delete()
    for device_id in grouped.get("medical_devices", set()):
        MedicalDevice.query.filter_by(device_id=device_id).delete()
    for theater_id in grouped.get("operating_theaters", set()):
        OperatingTheater.query.filter_by(theater_id=theater_id).delete()
    for room_id in grouped.get("rooms", set()):
        Room.query.filter_by(room_id=room_id).delete()
    for staff_id in grouped.get("medical_staff_specialties", set()):
        MedicalStaffSpecialty.query.filter_by(medical_staff_specialty_id=staff_id).delete()
    for staff_id in grouped.get("medical_staff", set()):
        MedicalStaff.query.filter_by(staff_id=staff_id).delete()
    for staff_id in grouped.get("nursing_staff", set()):
        NursingStaff.query.filter_by(staff_id=staff_id).delete()
    for staff_id in grouped.get("general_staff", set()):
        GeneralStaff.query.filter_by(staff_id=staff_id).delete()
    for patient_id in grouped.get("patients", set()):
        Patient.query.filter_by(patient_id=patient_id).delete()
    for staff_id in grouped.get("staff", set()):
        Staff.query.filter_by(staff_id=staff_id).delete()
    for medication_id in grouped.get("medications", set()):
        Medication.query.filter_by(medication_id=medication_id).delete()
    for specialty_id in grouped.get("medical_specialties", set()):
        MedicalSpecialty.query.filter_by(specialty_id=specialty_id).delete()
    for floor_id in grouped.get("floors", set()):
        Floor.query.filter_by(floor_id=floor_id).delete()
    DummyRegistry.query.delete()
    db.session.commit()
