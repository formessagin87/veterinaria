from app import create_app, db
from app.models.species import Species
from app.models.breed import Breed

def seed_data():
    # Crear la aplicación y contexto
    app = create_app()
    with app.app_context():
        # Asegurarse de que la base de datos esté creada
        db.create_all()

        species_data = [
            {
                "name": "Perro",
                "breeds": [
                    "Labrador Retriever",
                    "Bulldog",
                    "Pastor Alemán",
                    "Golden Retriever",
                    "Poodle",
                    "Beagle",
                    "Rottweiler",
                    "Yorkshire Terrier",
                    "Boxer",
                    "Dachshund",
                    "Siberian Husky",
                    "Great Dane",
                    "Doberman Pinscher",
                    "Shih Tzu",
                    "Australian Shepherd",
                    "Miniature Schnauzer",
                    "Cavalier King Charles Spaniel",
                    "Pomeranian",
                    "Chihuahua",
                    "Border Collie",
                    "Cocker Spaniel",
                    "Shetland Sheepdog",
                    "Bernese Mountain Dog",
                    "Bichon Frise",
                    "Cane Corso",
                    "Mastiff",
                    "Basset Hound",
                    "French Bulldog",
                    "German Shorthaired Pointer",
                    "Alaskan Malamute",
                    "Collie",
                    "Newfoundland",
                    "Australian Cattle Dog",
                    "English Springer Spaniel",
                    "Vizsla",
                    "Weimaraner",
                    "Staffordshire Bull Terrier",
                    "West Highland White Terrier",
                    "Rhodesian Ridgeback",
                    "Pug",
                    "Bloodhound",
                    "Chow Chow",
                    "Brittany",
                    "Whippet",
                    "Airedale Terrier",
                    "Scottish Terrier",
                    "Basenji",
                    "Samoyed",
                    "Miniature Pinscher",
                    "Great Pyrenees",
                    "Dalmatian",
                    "Norwegian Elkhound",
                    "American Staffordshire Terrier",
                    "Old English Sheepdog",
                    "Belgian Malinois",
                    "Pointer",
                    "Maltese",
                    "Havanese",
                    "Lhasa Apso",
                    "Keeshond",
                    "Wirehaired Pointing Griffon",
                    "American Cocker Spaniel",
                    "Flat-Coated Retriever",
                    "Irish Setter",
                    "Irish Wolfhound",
                    "Kuvasz",
                    "Saluki",
                    "Italian Greyhound",
                    "Leonberger",
                    "Japanese Chin",
                    "Schipperke",
                    "Silky Terrier",
                    "Pharaoh Hound",
                    "American Eskimo Dog",
                    "Australian Terrier",
                    "Bedlington Terrier",
                    "Borzoi",
                    "Cardigan Welsh Corgi",
                    "Dogue de Bordeaux",
                    "English Foxhound",
                    "Giant Schnauzer",
                    "Glen of Imaal Terrier",
                    "Ibizan Hound",
                    "Japanese Spitz",
                    "Kerry Blue Terrier",
                    "Mudi",
                    "Norfolk Terrier",
                    "Norwich Terrier",
                    "Puli",
                    "Sealyham Terrier",
                    "Soft Coated Wheaten Terrier",
                    "Stabyhoun",
                    "Tibetan Mastiff",
                    "Tibetan Spaniel",
                    "Xoloitzcuintli",
                    "Coton de Tulear",
                    "Brussels Griffon",
                    "English Toy Spaniel",
                    "Lowchen",
                    "Polish Lowland Sheepdog"
                ]
            },
            {
                "name": "Gato",
                "breeds": [
                    "Siamés",
                    "Persa",
                    "Maine Coon",
                    "Bengalí",
                    "Esfinge"
                ]
            },
            {
                "name": "Ave",
                "breeds": [
                    "Canario",
                    "Periquito",
                    "Cacatúa",
                    "Loro Amazonas"
                ]
            },
            {
                "name": "Pez",
                "breeds": [
                    "Betta",
                    "Goldfish",
                    "Tetra Neón",
                    "Pez Ángel"
                ]
            }
        ]

        # Agregar las especies y razas a la base de datos
        for species_item in species_data:
            # Verificar si la especie ya existe (ignorando mayúsculas y minúsculas si se requiere)
            species = Species.query.filter_by(name=species_item["name"]).first()
            if not species:
                species = Species(name=species_item["name"])
                db.session.add(species)
                db.session.flush()  # Para obtener el ID asignado a la nueva especie
            else:
                print(f"Especie '{species.name}' ya existe. Se actualizarán sus razas.")

            # Recorrer las razas para la especie
            for breed_name in species_item["breeds"]:
                # Verificar si la raza ya existe para esa especie
                breed = Breed.query.filter_by(name=breed_name, species_id=species.id).first()
                if not breed:
                    breed = Breed(name=breed_name, species_id=species.id)
                    db.session.add(breed)
                else:
                    print(f"La raza '{breed_name}' para la especie '{species.name}' ya existe. Se omite.")

        # Confirmar los cambios en la base de datos
        db.session.commit()
        print("Datos de especies y razas prellenados correctamente.")

if __name__ == "__main__":
    seed_data()
